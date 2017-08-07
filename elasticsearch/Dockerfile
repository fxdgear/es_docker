FROM centos:7

ARG ELASTIC_VERSION=5.5.0
ENV ELASTIC_VERSION ${ELASTIC_VERSION}

ENV ELASTIC_CONTAINER true
ENV PATH /usr/share/elasticsearch/bin:$PATH
ENV JAVA_HOME /usr/lib/jvm/jre-1.8.0-openjdk

RUN yum update -y && yum install -y java-1.8.0-openjdk-headless wget which curl jq bind-tools && yum clean all
RUN wget -O jq http://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64 && \
    chmod +x ./jq && \
    cp jq /usr/bin

RUN groupadd -g 1000 elasticsearch && adduser -u 1000 -g 1000 -d /usr/share/elasticsearch elasticsearch

WORKDIR /usr/share/elasticsearch

ENV URL_ROOT https://artifacts.elastic.co/downloads/elasticsearch
ENV TARBALL elasticsearch-$ELASTIC_VERSION.tar.gz

# Download and extract defined ES version. busybox tar can't strip leading dir.
RUN wget --progress=bar:force $URL_ROOT/$TARBALL && \
    tar zxf $TARBALL && \
    chown -R elasticsearch:elasticsearch elasticsearch-$ELASTIC_VERSION && \
    mv elasticsearch-$ELASTIC_VERSION/* . && \
    rmdir elasticsearch-$ELASTIC_VERSION && \
    rm $TARBALL

RUN set -ex && for esdirs in config data logs; do \
        mkdir -p "$esdirs"; \
        chown -R elasticsearch:elasticsearch "$esdirs"; \
    done

USER elasticsearch


COPY ./config config/
COPY es-docker bin/es-docker
COPY es-healthcheck bin/es-healthcheck

USER root
RUN chown elasticsearch:elasticsearch \
      config/elasticsearch.yml \
      config/log4j2.properties \
      config/x-pack/log4j2.properties \
      bin/es-docker && \
    chmod 0750 bin/es-docker

USER elasticsearch

HEALTHCHECK --interval=1s --retries=30 CMD ["/bin/bash", "bin/es-healthcheck"]

CMD ["/bin/bash", "bin/es-docker"]

EXPOSE 9200 9300
