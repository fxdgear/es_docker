import os
import json
import re

SUBSTITUTIONS = {
    'type': 'doc_type',
    'from': 'from_',
}

BASE_PATH = 'x-pack-elasticsearch/plugin/src/test/resources/rest-api-spec/api'

methods = {}

def wrap(txt, indent_more=True, indent=2):
    import textwrap

    tw = textwrap.TextWrapper(
            width=80,
            initial_indent=' ' * 4 * indent,
            subsequent_indent=' ' * 4 * indent + ('    ' if indent_more else ''),
            break_long_words=False
    )
    return '\n'.join(tw.wrap(txt))

for f in sorted(os.listdir(BASE_PATH)):
    name, ext = f.rsplit('.', 1)

    if ext != 'json' or name == '_common':
        continue

    with open(os.path.join(BASE_PATH, f)) as api_def:
        try:
            api = json.load(api_def)
        except:
            raise

    name, api = api.popitem()
    parsed = {}

    if 'parts' not in api['url']:
        api['url']['parts'] = {}

    if 'params' not in api['url']:
        api['url']['params'] = {}


    for key in SUBSTITUTIONS:
        for d in (api['url']['parts'], api['url']['params']):
            if key in d:
                d[SUBSTITUTIONS[key]] = d.pop(key)

    pos_params = []
    kw_params = []
    parts = []
    path = max(api['url']['paths'], key=lambda p: len(re.findall('\{([^}]+)\}', p)))
    for part in re.findall('\{([^}]+)\}', path):
        if part in SUBSTITUTIONS:
            part = SUBSTITUTIONS[part]
        desc = api['url']['parts'].get(part, {})
        parts.append(part)
        if desc.get('required'):
            pos_params.append(part)
        else:
            kw_params.append('%s=None' % part)

    if api.get('body'):
        if api['body'].get('required'):
            pos_params.append('body')
        else:
            kw_params.append('body=None')

        parsed['body'] = ', body=body'

        if api['body'].get('serialize', '') == 'bulk':
            parsed['body'] = ', body=self._bulk_body(body)'

        # inject body in the other params
        api['url']['parts']['body'] = {'description': api['body']['description']}
    else:
        parsed['body'] = ''

    part_docs = []
    for part in pos_params + [p.split('=', 1)[0] for p in kw_params]:
        desc = api['url']['parts'].get(part, {})
        part_docs.append(':arg %s: %s%s' % (part, desc.get('description'), ", default %r" % desc['default'] if desc.get("default") else ''))

    parsed['parts_raw'] = ', '.join(parts)


    params = map(repr, map(str, sorted([n for n in api['url']['params']  if n not in pos_params and '%s=None' %n not in kw_params ])))
    parsed['query_params'] = wrap('@query_params(%s)' % ', '.join(params), indent=1)

    parsed['method'] = api['methods'][0]

    # TODO: add an optional if default is None
    parsed['url'] = re.sub(r'\{[^}]+\}', '%s', api['url']['path'])

    parsed['params'] = ', '.join(pos_params + kw_params)
    if parsed['params']:
        parsed['params'] += ', '

    param_docs = [
        ':arg %s: %s%s%s' % (
            n, value.get('description', ''),
            ", default %r" % value['default'] if "default" in value else '',
            ', valid choices are: %s ' % ', '.join(map(repr, value['options'])) if 'options' in value else ''

            )
        for (n, value) in sorted(api['url']['params'].items())
        if n not in pos_params and '%s=None' %n not in kw_params
    ]

    parsed['docstring'] = """
        `<%s>`_""" % api.get("documentation", '').replace('/5.x/', '/current/').replace('/1.4/', '/current/')

    params = '\n'.join(map(wrap, part_docs + param_docs))
    if params:
        parsed['docstring'] += """\n\n%s""" % params

    parts = []
    dynamic = False
    for part in path.split('/'):
        if not part:
            continue

        # dynamic
        if part[0] == '{':
            part = part[1:-1]
            parts.append(SUBSTITUTIONS.get(part, part))
            dynamic = True
        else:
            parts.append("'%s'" % part)

    if dynamic:
        parsed['url'] = '_make_path(%s)' % ', '.join(parts)
    else:
        parsed['url'] = "'%s'" % path

    parent = 'object'
    namespace = '__init__'
    if '.' in name:
        namespace, name = name.rsplit('.', 1)
        parent = 'NamespacedClient'

    if namespace == 'xpack':
        namespace = 'xpack/__init__'
    namespace = namespace.replace('.', '/')

    parsed['name'] = name
    if namespace not in methods:
        methods[namespace] = (parent, {})

    if len(pos_params) == 1:
        parsed['code'] = '        if %s in SKIP_IN_PATH:\n            raise ValueError("Empty value passed for a required argument \'%s\'.")\n' % (pos_params[0], pos_params[0])
    elif pos_params:
        parsed['code'] = '        for param in (%s):\n            if param in SKIP_IN_PATH:\n                raise ValueError("Empty value passed for a required argument.")\n' % ', '.join(pos_params)
    else:
        parsed['code'] = ''

    parsed['code'] += wrap("return self.transport.perform_request('%(method)s', %(url)s, params=params%(body)s)" % parsed)
    methods[namespace][1][name] = '''\
%(query_params)s
    def %(name)s(self, %(params)sparams=None):
        """%(docstring)s
        """
%(code)s
''' % parsed


orders = {}
descriptions = {}

for namespace in methods:
    if os.path.exists('orig/%s.py' % namespace):
        with open('orig/%s.py' % namespace) as f:
            defined_apis = re.findall(r'\n    def ([a-z_]+)\([^\n]*\n *"""\n *([\w\W]*?)(?:`<|""")', f.read(), re.MULTILINE)
            descriptions[namespace] = dict(map(lambda i: (i[0], i[1].strip()), defined_apis))
            orders[namespace] = list(map(lambda x: x[0], defined_apis))

for namespace, (parent, apis) in methods.items():
    if '/' in namespace:
        dir, _ = namespace.rsplit('/', 1)
        if not os.path.exists('out/%s' % dir):
            os.mkdir('out/%s' % dir)
    with open('out/%s.py' % namespace, 'w') as fout:
        if namespace != '__init__':
            fout.write('from .utils import NamespacedClient, query_params, _make_path, SKIP_IN_PATH\n\n')
            fout.write('class %sClient(%s):\n' % (namespace.split('/')[-1].title(), parent))
        else:
            fout.write('class Elasticsearch(object):\n')

        def ind(i):
            name, value = i
            try:
                return orders[namespace].index(name)
            except (ValueError, KeyError):
                return len(orders.get(namespace, []))

        for name, definition in sorted(apis.items(), key=ind):
            if name in descriptions.get(namespace, {}):
                definition = definition.replace('"""', '"""\n        %s' % descriptions[namespace][name], 1)
            fout.write(definition)
            fout.write('\n')

