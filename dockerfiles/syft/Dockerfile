FROM alpine:3.19.0
LABEL version="1.0"
LABEL description="Custom Syft image for SBOM genration"

ENV SYFT_VERSION=0.101.1
RUN apk --no-cache add curl tar
RUN curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin v${SYFT_VERSION}

WORKDIR /artifacts

ENTRYPOINT ["syft"]
