FROM kibana:4

COPY kb-healthcheck bin/kb-healthcheck

RUN apt-get update && apt-get -y install curl jq

HEALTHCHECK --interval=10s CMD ["/bin/bash", "bin/kb-healthcheck"]
