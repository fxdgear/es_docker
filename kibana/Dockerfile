FROM centos:7
EXPOSE 5601

ARG ELASTIC_VERSION=local
ENV ELASTIC_VERSION ${ELASTIC_VERSION}

ENV URL_ROOT https://artifacts.elastic.co/downloads/kibana
ENV KIBANA_DIR kibana-$ELASTIC_VERSION-linux-x86_64
ENV TARBALL kibana-$ELASTIC_VERSION-linux-x86_64.tar.gz

# Add Reporting dependencies.
RUN yum update -y && yum install -y fontconfig wget freetype curl && yum clean all
RUN wget -O jq http://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64 && \
    chmod +x ./jq && \
    cp jq /usr/bin

WORKDIR /usr/share/kibana
RUN curl -Ls $URL_ROOT/kibana-$ELASTIC_VERSION-linux-x86_64.tar.gz | tar --strip-components=1 -zxf - && \
    ln -s /usr/share/kibana /opt/kibana

ENV ELASTIC_CONTAINER true
ENV PATH=/usr/share/kibana/bin:$PATH

# Set some Kibana configuration defaults.
ADD kibana/config.yml /usr/share/kibana/config/

# Add the launcher/wrapper script. It knows how to interpret environment
# variables and translate them to Kibana CLI options.
ADD kibana/kibana-docker /usr/local/bin/
COPY kibana/kb-healthcheck bin/kb-healthcheck

# Add a self-signed SSL certificate for use in examples.
# ADD ssl/kibana.example.org.* /usr/share/kibana/config/

# Provide a non-root user to run the process.
RUN groupadd --gid 1000 kibana && \
    useradd --uid 1000 --gid 1000 \
      --home-dir /usr/share/kibana --no-create-home \
      kibana

RUN chown kibana:kibana \
    /usr/local/bin/kibana-docker \
    bin/kb-healthcheck && \
    chmod 0750 /usr/local/bin/kibana-docker

USER kibana

HEALTHCHECK --interval=10s CMD ["/bin/bash", "bin/kb-healthcheck"]
CMD /usr/local/bin/kibana-docker
