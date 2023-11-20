SHELL := /bin/bash
ARTESCA_VERSION = "2.1.0"
ARTESCA_DOWNLOAD_BASE_URL = https://packages.scality.com/Artesca
ARTIFACTS_URL = ${ARTESCA_DOWNLOAD_BASE_URL}/${ARTESCA_VERSION}/artifacts
ARTIFACTS_OS_URL = ${ARTESCA_DOWNLOAD_BASE_URL}/${ARTESCA_VERSION}/os
ARTIFACTS_ARTESCA_LIST = artesca-base.iso artesca-base-repo.iso metalk8s.iso xcore.iso zenko-base.iso zenko.iso
ARTIFACTS_ARTESCA_OS = artesca-os.iso
ARTIFACTS_ARTESCA_FULL_LIST = ${ARTIFACTS_ARTESCA_LIST} ${ARTIFACTS_ARTESCA_OS}
SUMFILE_ARTESCA_OS = artesca-os.iso.sha256sum
SUMFILE_ARTESCA_INSTALLER = SHA256SUM
IMAGE_NAME := scan_artesca

.PHONY: download_artifacts 

all: download_artifacts scan_run clean_tmp

create_artifacts_dir:
	@echo "Create artifacts directory"
	@mkdir -p artifacts

create_results_dir:
	@echo "Create results directory"
	@mkdir -p results

download_artifacts: create_artifacts_dir
	@read -p "Enter username for packages.scality.com: " username; \
	read -s -p "Enter password for packages.scality.com: " password; \
	printf "\n"; \
	for artifact in $(ARTIFACTS_ARTESCA_LIST); do \
		echo "Downloading $$artifact"; \
		curl -s -Lo artifacts/$$artifact ${ARTIFACTS_URL}/$$artifact -u "$$username:$$password"; \
	done; \
	echo "Downloading $(ARTIFACTS_ARTESCA_OS)"; \
	curl -s -Lo artifacts/${ARTIFACTS_ARTESCA_OS} ${ARTIFACTS_OS_URL}/${ARTIFACTS_ARTESCA_OS} -u "$$username:$$password"; \
	echo "Downloading sumfile for $(ARTIFACTS_ARTESCA_OS)"; \
	curl -s -Lo artifacts/${SUMFILE_ARTESCA_OS} ${ARTIFACTS_OS_URL}/${SUMFILE_ARTESCA_OS} -u "$$username:$$password"; \
	echo "Check download integrity"; \
	cd artifacts && sha256sum -c ${SUMFILE_ARTESCA_OS} \

mount_iso:
	for artifact in $(ARTIFACTS_ARTESCA_FULL_LIST); do \
		mkdir -p artifacts/mnt/$$artifact; \
		echo "Mounting $$artifact"; \
		fuseiso artifacts/$$artifact artifacts/mnt/$$artifact; \
	done

umount_volumes:
	@for artifact in $(ARTIFACTS_ARTESCA_FULL_LIST); do \
		echo "Unmounting $$artifact"; \
		fusermount -u artifacts/mnt/$$artifact; \
	done

generate_scan_script:
	@echo "#!/bin/sh" > tmp/scan.sh; \
	echo "for artifact in \$$artifacts_to_scan; do" >> tmp/scan.sh; \
	echo "  echo \"Scanning \$$artifact\"; \\" >> tmp/scan.sh; \
	echo "  syft packages -q -o syft-json=results/\syft_$$(basename \$$artifact).json -o cyclonedx-json=results/\syft_cyclonedx_$$(basename \$$artifact).json \$$artifact; \\" >> tmp/scan.sh; \
	echo "  grype sbom:/results/\syft_$$(basename \$$artifact).json -o cyclonedx-json >> /results/\grype_cyclonedx_$$(basename \$$artifact).json; \\" >> tmp/scan.sh; \
	echo "  grype sbom:/results/\syft_$$(basename \$$artifact).json -o table >> /results/\grype_table_$$(basename \$$artifact).txt; \\" >> tmp/scan.sh; \
	echo "done" >> tmp/scan.sh
	@chmod +x tmp/scan.sh

generate_docker_file:
	@echo "FROM rockylinux/rockylinux:9" > tmp/Dockerfile; \
	echo "ENV artifacts_to_scan \"${ARTIFACTS_ARTESCA_FULL_LIST}\"" >> tmp/Dockerfile; \
	for artifact in $(ARTIFACTS_ARTESCA_FULL_LIST); do \
		echo "VOLUME /$$artifact" >> tmp/Dockerfile; \
		echo "COPY artifacts/mnt/$$artifact /$$artifact" >> tmp/Dockerfile; \
	done
	echo "RUN dnf install -y tar" >> tmp/Dockerfile; \
	echo "RUN curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin" >> tmp/Dockerfile; \
	echo "RUN curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin" >> tmp/Dockerfile; \
    echo "COPY tmp/scan.sh /usr/local/bin/scan.sh" >> tmp/Dockerfile; \
    echo "CMD [\"sh\", \"/usr/local/bin/scan.sh\"]" >> tmp/Dockerfile; \

generate_image: mount_iso generate_scan_script generate_docker_file
	docker build -t $(IMAGE_NAME) . -f tmp/Dockerfile
	$(MAKE) umount_volumes

scan_run: create_results_dir generate_image
	docker run --rm -v $(PWD)/results:/results $(IMAGE_NAME)

clean_tmp:
	rm -rf tmp/Dockerfile
	rm -rf tmp/scan.sh
