ARG PYTHON_VERSION=3
FROM python:${PYTHON_VERSION}
RUN apt-get update && apt-get install git curl
RUN pip install ipdb python-dateutil GitPython

RUN git clone https://github.com/elastic/elasticsearch.git /code/elasticsearch
WORKDIR /code/elasticsearch
RUN git pull
COPY wait-for-elasticsearch.sh /code/wait-for-elasticsearch.sh
COPY elasticsearch-py /code/elasticsearch-py
WORKDIR /code/elasticsearch-py
RUN pip install .[develop]
RUN python setup.py develop
CMD ["/code/wait-for-elasticsearch.sh", "http://elasticsearch:9200", "--", "python", "setup.py", "test"]
