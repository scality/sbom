FROM alpine:3.19.0
LABEL version="1.0"
LABEL description="Custom Grype image for SBOM vulnerability scanning"

ENV GRYPE_VERSION=0.74.2
RUN apk --no-cache add curl tar
RUN curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin v${GRYPE_VERSION}

WORKDIR /results

ENTRYPOINT ["grype"]
