FROM mcr.microsoft.com/devcontainers/base:noble

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install --no-install-recommends -y \
        acl \
        apt-transport-https \
        bash-completion \
        curl \
        git \
        libmagic1 \
        libsqlite3-dev \
        python3 \
        python3-pip \
        python3-venv \
        p7zip-full \
        skopeo \
        tmux \
        vim \
        && \
    apt-get clean

USER vscode

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Create virtual environment
ENV VIRTUAL_ENV=/home/vscode/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt /tmp/requirements.txt

# Install python libs in the virtual environment
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt
