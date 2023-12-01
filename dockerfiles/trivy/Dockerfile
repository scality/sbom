FROM alpine:3.18.5
LABEL version="1.0"
LABEL description="Custom Trivy image for vulnerability scanning"

ENV TRIVY_VERSION=0.47.0
RUN apk --no-cache add curl tar
RUN curl -sSfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin v${TRIVY_VERSION}


WORKDIR /images

ENTRYPOINT ["trivy"]
