FROM elasticsearch:2.4-alpine

COPY es-docker bin/es-docker
COPY es-healthcheck bin/es-healthcheck

RUN apk add --update curl && \
    rm -rf /var/cache/apk/*

USER root

RUN chown elasticsearch:elasticsearch bin/es-docker && \
    chmod 0750 bin/es-docker

USER elasticsearch

HEALTHCHECK --interval=1s --retries=30 CMD ["/bin/bash", "bin/es-healthcheck"]

CMD ["/bin/bash", "bin/es-docker"]