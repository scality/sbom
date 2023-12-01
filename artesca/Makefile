SHELL := /bin/bash
ARTESCA_VERSION := "2.1.1"
METALK8S_VERSION := "126.0.2"
ARTESCA_DOWNLOAD_BASE_URL := https://packages.scality.com/Artesca
ARTIFACTS_URL := ${ARTESCA_DOWNLOAD_BASE_URL}/${ARTESCA_VERSION}/artifacts
ARTIFACTS_OS_URL := ${ARTESCA_DOWNLOAD_BASE_URL}/${ARTESCA_VERSION}/os
ARTIFACTS_ARTESCA_LIST := artesca-base.iso artesca-base-repo.iso metalk8s.iso xcore.iso zenko-base.iso zenko.iso
ARTIFACTS_ARTESCA_OS := artesca-os.iso
ARTIFACTS_FULL_LIST := ${ARTIFACTS_ARTESCA_LIST} ${ARTIFACTS_ARTESCA_OS}
SUMFILE_ARTESCA_OS := artesca-os.iso.sha256sum
SUMFILE_ARTESCA_INSTALLER := SHA256SUM
GITHUB_REPO_ARTESCA := artesca
GITHUB_REPO_METALK8S := metalk8s
IMAGE_SYFT := sbom_syft
IMAGE_SKOPEO := sbom_skopeo
IMAGE_TRIVY := sbom_trivy
ARTIFACTS_DOWNLOAD_DIR := artifacts
REPO_DOWNLOAD_DIR := $(ARTIFACTS_DOWNLOAD_DIR)/repo
ARTIFACTS_MOUNT_DIR := $(ARTIFACTS_DOWNLOAD_DIR)/mnt
IMAGES_EXPORT_DIR := $(ARTIFACTS_DOWNLOAD_DIR)/images
RESULTS_DIR := results/artesca

.PHONY: download_artifacts create_artifacts_dir create_results_dir

all: download_artifacts scan_image scan_artesca clean

create_artifacts_dir:
	@echo "Create artifacts directory"
	@mkdir -p $(REPO_DOWNLOAD_DIR)

create_results_dir:
	@echo "Create results directory"
	@mkdir -p $(RESULTS_DIR)

download_artifacts: create_artifacts_dir
	# @read -p "Enter username for packages.scality.com: " username; \
	# read -s -p "Enter password for packages.scality.com: " password; \
	# printf "\n"; \
	# for artifact in $(ARTIFACTS_ARTESCA_LIST); do \
	# 	echo "Downloading artifact : $$artifact"; \
	# 	curl -s -Lo $(ARTIFACTS_DOWNLOAD_DIR)/$$artifact ${ARTIFACTS_URL}/$$artifact -u "$$username:$$password"; \
	# done; \
	# echo "Downloading artifact : $(ARTIFACTS_ARTESCA_OS)"; \
	# curl -s -Lo $(ARTIFACTS_DOWNLOAD_DIR)/${ARTIFACTS_ARTESCA_OS} ${ARTIFACTS_OS_URL}/${ARTIFACTS_ARTESCA_OS} -u "$$username:$$password"; \
	# echo "Downloading sumfile for $(ARTIFACTS_ARTESCA_OS)"; \
	# curl -s -Lo $(ARTIFACTS_DOWNLOAD_DIR)/${SUMFILE_ARTESCA_OS} ${ARTIFACTS_OS_URL}/${SUMFILE_ARTESCA_OS} -u "$$username:$$password"; \
	echo "Downloading repo : $(GITHUB_REPO_ARTESCA)"; \
	git clone git@github.com:scality/$(GITHUB_REPO_ARTESCA).git $(REPO_DOWNLOAD_DIR)/$(GITHUB_REPO_ARTESCA) --branch $(ARTESCA_VERSION) ; \
	echo "Downloading repo : $(GITHUB_REPO_METALK8S)"; \
	git clone git@github.com:scality/$(GITHUB_REPO_METALK8S).git $(REPO_DOWNLOAD_DIR)/$(GITHUB_REPO_METALK8S) --branch $(METALK8S_VERSION) ; \
	echo "Check download integrity"; \
	cd $(ARTIFACTS_DOWNLOAD_DIR) && sha256sum -c ${SUMFILE_ARTESCA_OS}; \

mount_iso:
	@for artifact in $(ARTIFACTS_FULL_LIST); do \
		artifact_name=$$(basename $$artifact .iso); \
		mkdir -p $(ARTIFACTS_MOUNT_DIR)/$$artifact_name; \
        if mountpoint -q $(ARTIFACTS_MOUNT_DIR)/$$artifact_name; then \
            echo "$(ARTIFACTS_MOUNT_DIR)/$$artifact_name is already mounted"; \
        else \
            if [ $$(id -u) -ne 0 ]; then \
                sudo mount -o loop $(ARTIFACTS_DOWNLOAD_DIR)/$$artifact $(ARTIFACTS_MOUNT_DIR)/$$artifact_name; \
            else \
                mount -o loop $(ARTIFACTS_DOWNLOAD_DIR)/$$artifact $(ARTIFACTS_MOUNT_DIR)/$$artifact_name; \
            fi; \
        fi; \
	done

umount_iso:
	@for artifact in $(ARTIFACTS_FULL_LIST); do \
		artifact_name=$$(basename $$artifact .iso); \
		echo "Unmounting $$artifact"; \
		if [ $$(id -u) -ne 0 ]; then \
			sudo umount $(ARTIFACTS_MOUNT_DIR)/$$artifact_name; \
		else \
			umount $(ARTIFACTS_MOUNT_DIR)/$$artifact_name; \
		fi; \
	done

generate_image:
	@docker build -t $(IMAGE_SYFT) . -f ../dockerfiles/syft/Dockerfile
	@docker build -t $(IMAGE_SKOPEO) . -f ../dockerfiles/skopeo/Dockerfile
	@docker build -t $(IMAGE_TRIVY) . -f ../dockerfiles/trivy/Dockerfile

scan_image: create_results_dir generate_image mount_iso
	@for image_dir in `find $(ARTIFACTS_MOUNT_DIR) -name images -type d`; do \
		for dir in `find $$image_dir -mindepth 2 -maxdepth 2 -type d`; do \
			image_name=$$(echo $$dir | awk -F "/" '{print $$(NF-1)}'); \
			image_version=$$(echo $$dir | awk -F "/" '{print $$(NF)}'); \
			image_source=$$(echo $$dir | awk -F "/" '{print $$(NF-3)}'); \
			echo "Converting $$image_name $$image_version from $$image_source"; \
			docker run --rm -v $(PWD)/$$dir:/imported_image -v $(PWD)/$(IMAGES_EXPORT_DIR):/exported_image $(IMAGE_SKOPEO) copy --format v2s2 dir://imported_image oci:/exported_image/$$image_source\_$$image_name\_$$image_version; \
			echo "Scanning $$image_name $$image_version from $$image_source"; \
			docker run --rm -v $(PWD)/$(IMAGES_EXPORT_DIR):/images $(IMAGE_TRIVY) image --input /images/$$image_source\_$$image_name\_$$image_version -f json > $(RESULTS_DIR)/image_$$image_source\_$$image_name\_$$image_version.json; \
		done; \
	done; \

scan_artesca: create_results_dir generate_image mount_iso
	@for artifact_path in `find $(ARTIFACTS_MOUNT_DIR) -mindepth 1 -maxdepth 1 -type d`; do \
		artifact_name=`basename $$artifact_path`; \
		echo "Scanning ISO $$artifact_name"; \
		docker run --rm -v $(PWD)/$(ARTIFACTS_MOUNT_DIR)/$$artifact_name:/artifacts $(IMAGE_SYFT) -o cyclonedx-json /artifacts > $(RESULTS_DIR)/iso_$$artifact_name.json; \
	done; \
	for repo in $(GITHUB_REPO_ARTESCA_LIST); do \
		echo "Scanning $$repo"; \
		for package_path in `find $(REPO_DOWNLOAD_DIR)/$$repo -name package-lock.json`; do \
			package_directory=$$(dirname $$package_path); \
			package_name=$$(cat $$package_path | sed -n '2 p' | awk -F "\"" '{print $$4}' | sed 's/\//-/'); \
			echo "Scanning $$package_name" found in $$package_directory; \
			docker run --rm -v $(PWD)/$$package_directory:/artifacts $(IMAGE_SYFT) -o cyclonedx-json /artifacts/package-lock.json > $(RESULTS_DIR)/repo_$$repo\_npm_$$package_name.json; \
		done; \
		for package_path in `find $(REPO_DOWNLOAD_DIR)/$$repo -name go.mod`; do \
			package_directory=$$(dirname $$package_path); \
			package_name=$$(cat $$package_path | sed -n '1 p' | awk -F "/" '{print $$(NF-1) "_" $$NF}'); \
			echo "Scanning $$package_name" found in $$package_directory; \
			docker run --rm -v $(PWD)/$$package_directory:/artifacts $(IMAGE_SYFT) -o cyclonedx-json /artifacts/go.mod > $(RESULTS_DIR)/repo_$$repo\_go_$$package_name.json; \
		done; \
		for package_path in `find $(REPO_DOWNLOAD_DIR)/$$repo -name requirements.txt`; do \
			package_directory=$$(dirname $$package_path); \
			package_name=$$(echo $$package_path | awk -F "/" '{print $$(NF-1)}'); \
			echo "Scanning $$package_name" found in $$package_directory; \
			docker run --rm -v $(PWD)/$$package_directory:/artifacts $(IMAGE_SYFT) -o cyclonedx-json /artifacts/requirements.txt > $(RESULTS_DIR)/repo_$$repo\_python_$$package_name.json; \
		done; \
	done; \

clean: umount_iso
	if [ $$(id -u) -ne 0 ]; then \
		sudo rm -rf $(ARTIFACTS_DOWNLOAD_DIR)/* ; \
	else \
		rm -rf $(ARTIFACTS_DOWNLOAD_DIR)/* ; \
	fi; \
