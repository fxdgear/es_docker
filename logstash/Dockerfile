FROM centos:7

ARG ELASTIC_VERSION=5.5.0
ENV ELASTIC_VERSION ${ELASTIC_VERSION}

# https://artifacts.elastic.co/downloads/logstash/logstash-5.5.1.tar.gz
ENV URL_ROOT https://artifacts.elastic.co/downloads/logstash
ENV PACK_URL https://artifacts.elastic.co/downloads/logstash-plugins
# Install Java and the "which" command, which is needed by Logstash's shell
# scripts.
RUN yum update -y && yum install -y java-1.8.0-openjdk-devel which && \
    yum clean all

# Provide a non-root user to run the process.
RUN groupadd --gid 1000 logstash && \
    adduser --uid 1000 --gid 1000 \
      --home-dir /usr/share/logstash --no-create-home \
      logstash

# Add Logstash itself.
RUN curl -Lo - $URL_ROOT/logstash-$ELASTIC_VERSION.tar.gz | \
    tar zxf - -C /usr/share && \
    mv /usr/share/logstash-$ELASTIC_VERSION /usr/share/logstash && \
    chown --recursive logstash:logstash /usr/share/logstash/ && \
    ln -s /usr/share/logstash /opt/logstash

ENV ELASTIC_CONTAINER true
ENV PATH=/usr/share/logstash/bin:$PATH

# Provide a minimal configuration, so that simple invocations will provide
# a good experience.
ADD logstash/logstash.yml logstash/log4j2.properties /usr/share/logstash/config/
ADD logstash/pipeline/default.conf /usr/share/logstash/pipeline/logstash.conf
RUN chown --recursive logstash:logstash /usr/share/logstash/config/ /usr/share/logstash/pipeline/

# Ensure Logstash gets a UTF-8 locale by default.
ENV LANG='en_US.UTF-8' LC_ALL='en_US.UTF-8'

# Place the startup wrapper script.
ADD logstash/docker-entrypoint /usr/local/bin/
RUN chmod 0755 /usr/local/bin/docker-entrypoint

USER logstash

RUN cd /usr/share/logstash && LOGSTASH_PACK_URL=$PACK_URL logstash-plugin install logstash-input-http

ADD logstash/build/env2yaml/env2yaml /usr/local/bin/

EXPOSE 9600 5044

ENTRYPOINT ["/usr/local/bin/docker-entrypoint"]
