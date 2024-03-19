FROM mcr.microsoft.com/devcontainers/base:jammy

RUN export DEBIAN_FRONTEND=noninteractive && \
    curl -O -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh && \
    sudo sh install.sh -b /usr/local/bin

RUN export DEBIAN_FRONTEND=noninteractive && \
    curl -O -sSfL https://aquasecurity.github.io/trivy-repo/deb/public.key && \
    sudo apt-key add public.key && \
    echo deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main | tee -a /etc/apt/sources.list.d/trivy.list

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install --no-install-recommends -y \
        acl \
        apt-transport-https \
        bash-completion \
        build-essential \
        curl \
        git \
        gnupg lsb-release \
        isomd5sum \
        make \
        p7zip-full \
        skopeo \
        tmux \
        trivy \
        vim \
        && \
    apt-get clean
USER vscode
