FROM mcr.microsoft.com/devcontainers/base:jammy

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install --no-install-recommends -y \
        acl \
        apt-transport-https \
        bash-completion \
        curl \
        git \
        python3-pip \
        p7zip-full \
        skopeo \
        tmux \
        vim \
        && \
    apt-get clean
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r /tmp/requirements.txt
USER vscode