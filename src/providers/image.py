"""Image provider for SBOM generation."""

import os
import pathlib
import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from modules.convert import check_mediatype, convert_image_to_oci
from scanners.syft import SyftScanner
from scanners.grype import GrypeScanner
from .base import BaseProvider


class ImageInfo(BaseModel):
    """
    ## Image information model.
    ### Attributes:
        - name: Name of the image
        - version: Version of the image
        - path: Path to the image
        - source: Source of the image
        - excluded: Exclusion status of the image
    """

    name: str = Field(..., min_length=1)
    version: str
    path: str
    source: str = ""
    excluded: bool = False


class ImageProvider(BaseProvider):
    """Provider for container images."""

    def __init__(self, inputs: Dict[str, Any]):
        super().__init__(inputs)
        self.image_path = inputs.get("image")
        self.excluded_mediatypes = self._parse_excluded_types()

    def sbom(self, inputs: Dict[str, Any] = None) -> str:
        """
        ## Generate SBOM for an image or directory of images.
        ### Args:
            inputs: Optional dictionary of input parameters
        ### Returns:
            Dictionary or string depending on the scan result (single image or directory)
        """
        inputs = inputs or self.inputs
        target = inputs.get("target", self.target)

        # Determine if we're dealing with a single image or directory
        return (
            self._scan_single_image(target)
            if not os.path.isdir(target) or not self._contains_images(target)
            else self._scan_image_directory(target)
        )

    def vuln(self, sbom_path: str) -> Dict:
        """
        ## Scan for vulnerabilities in the generated SBOM.
        ### Args:
            sbom_path: Path to the generated SBOM file
        ### Returns:
            Dictionary with vulnerability scan results
        """
        # Check if it's a single file or a results dictionary
        if isinstance(sbom_path, str) and os.path.isfile(sbom_path):
            return self._scan_single_vuln(sbom_path)

        # Handle the dictionary results case (multiple images)
        return self._scan_multiple_vulns(sbom_path)

    def _parse_excluded_types(self) -> List[str]:
        """
        ## Parse excluded media types from inputs.
        ### Args:
            None
        ### Returns:
            List of excluded media types
        """
        excluded_types = self.inputs.get("exclude_mediatypes")
        return excluded_types.split(",") if excluded_types else []

    @staticmethod
    def _contains_images(directory: str) -> bool:
        """
        ## Check if directory contains image subdirectories.
        ### Args:
            directory: Path to the directory
        ### Returns:
            True if directory contains image subdirectories, False otherwise
        """
        if os.path.exists(os.path.join(directory, "images")):
            return True

        return any(
            os.path.isdir(os.path.join(directory, d)) for d in os.listdir(directory)
        )

    def _scan_single_image(self, target: str) -> str:
        """
        ## Scan a single image.
        ### Args:
            target: Path to the image
        ### Returns:
            str: Path to the generated SBOM file
        """
        # Extract image name and version for naming
        image_name = ""
        image_version = "latest"
        # Initialize image_with_path with the target
        image_with_path = target

        # Handle Docker image references
        if ":" in target:
            parts = target.split(":")
            image_with_path = parts[0]
            image_version = parts[1]

        # For output file, keep short name
        if "/" in image_with_path:
            image_name = image_with_path.split("/")[-1]
            # Strip file extensions (.tar, .tar.gz, etc.)
            image_name = os.path.splitext(image_name)[0]
            # Handle double extensions like .tar.gz
            if image_name.endswith(".tar"):
                image_name = os.path.splitext(image_name)[0]
        else:
            image_name = image_with_path
            # Also strip extensions if it's a direct filename
            if "." in image_name and not image_name.startswith("."):
                image_name = os.path.splitext(image_name)[0]
                # Handle double extensions
                if image_name.endswith(".tar"):
                    image_name = os.path.splitext(image_name)[0]

        # Set scanner args - only pass metadata, not output filename
        scanner_args = {
            "target": target,
            "target_metadata": {
                "image_name": image_name,
                "image_version": image_version,
            },
        }

        # Only add name/version if explicitly provided in inputs
        if self.name:
            scanner_args["name"] = self.name

        if self.version:
            scanner_args["version"] = self.version

        # Run scanner
        result = SyftScanner().scan(target, scanner_args)
        return result.get("sbom_path")

    def _scan_image_directory(self, target: str) -> Dict:
        """
        ## Scan a directory containing multiple images.
        ### Args:
            target: Path to the directory containing images
        ### Returns:
            Dictionary with scan results
        """
        # Setup working directories
        convert_dir = pathlib.Path("/tmp/images")
        os.makedirs(convert_dir, exist_ok=True)

        # Find the root directory for images
        image_dir = self._find_image_root(target)
        logging.info("Scanning images directory: %s", image_dir)

        if not image_dir or not os.path.isdir(image_dir):
            raise ValueError(f"No valid images directory found at {image_dir}")

        try:
            # Discover images
            images = self._discover_images(image_dir, target)

            if not images:
                logging.info("No images discovered to scan")
                return {"success": True, "scanned_images": [], "results": {}}

            # Scan images
            results = self._scan_images(images, convert_dir)

            return {
                "success": True,
                "scanned_images": results.keys(),
                "results": results,
            }
        except RuntimeError as error:
            logging.error("Error scanning image directory: %s", error)
            return {"success": False, "error": str(error)}

    def _find_image_root(self, target: str) -> str:
        """
        ## Find the root directory containing images.
        ### Args:
            target: Path to the target directory
        ### Returns:
            Path to the images directory or the target itself if not found
        """
        images_dir = os.path.join(target, "images")
        return images_dir if os.path.exists(images_dir) else target

    def _discover_images(self, image_dir: str, source: str) -> List[ImageInfo]:
        """
        ## Discover and catalog images in directory.
        ### Args:
            image_dir: Path to the directory containing images
            source: Source name for the images
        ### Returns:
            List of ImageInfo objects representing discovered images
        """
        source_name, image_name = self._get_clean_names(source, image_dir)

        # Try finding direct versions first
        direct_images = self._find_direct_versions(image_dir, source_name, image_name)

        if direct_images:
            return direct_images

        # Fall back to nested discovery
        return self._find_nested_versions(image_dir, source_name)

    def _get_clean_names(self, source: str, image_dir: str) -> tuple:
        """
        ## Extract clean source and image names from paths.
        ### Args:
            source: Source path
            image_dir: Image directory path
        ### Returns:
            Tuple of cleaned source and image names
        """
        source_clean = source.rstrip("/")
        image_dir_clean = image_dir.rstrip("/")

        source_name = os.path.basename(source_clean) or "unknown"
        logging.info("Source name: %s", source_name)

        image_name = os.path.basename(image_dir_clean) or "unknown"
        logging.info("Image name: %s", image_name)

        return source_name, image_name

    def _find_direct_versions(
        self, image_dir: str, source_name: str, image_name: str
    ) -> List[ImageInfo]:
        """
        ## Find version directories directly under the image directory.
        ### Args:
            image_dir: Path to the image directory
            source_name: Source name for the images
            image_name: Image name
        ### Returns:
            List of ImageInfo objects representing discovered images
        ### Notes:
            - This method looks for version directories directly under the image directory.
            - It also checks for nested image/version structures.
            - If no direct versions are found, it falls back to nested discovery.
        """
        images = []

        # Check for nested image/version structure
        for item in os.listdir(image_dir):
            image_subdir = os.path.join(image_dir, item)
            if not os.path.isdir(image_subdir):
                continue

            # Look for version subdirectories
            for subitem in os.listdir(image_subdir):
                version_dir = os.path.join(image_subdir, subitem)
                if not os.path.isdir(version_dir):
                    continue

                # Collect image info
                img_name = item
                img_version = subitem
                is_excluded = check_mediatype(version_dir, self.excluded_mediatypes)

                logging.info("Found nested image: %s:%s", img_name, img_version)

                images.append(
                    ImageInfo(
                        name=img_name,
                        version=img_version,
                        path=version_dir,
                        source=source_name,
                        excluded=is_excluded,
                    )
                )

        # If no nested images, check for version directories
        if not images:
            for item in os.listdir(image_dir):
                version_dir = os.path.join(image_dir, item)
                if os.path.isdir(version_dir) and (
                    item.startswith("v") or any(c.isdigit() for c in item)
                ):
                    img_version = item
                    is_excluded = check_mediatype(version_dir, self.excluded_mediatypes)

                    logging.info("Found direct version: %s:%s", image_name, img_version)

                    images.append(
                        ImageInfo(
                            name=image_name,
                            version=img_version,
                            path=version_dir,
                            source=source_name,
                            excluded=is_excluded,
                        )
                    )

        return images

    def _find_nested_versions(
        self, image_dir: str, source_name: str
    ) -> List[ImageInfo]:
        """
        ## Find version directories in nested structure.
        ### Args:
            image_dir: Path to the image directory
            source_name: Source name for the images
        ### Returns:
            List of ImageInfo objects representing discovered images
        ### Notes:
            - This method looks for version directories in a nested structure.
            - It checks for excluded media types and logs the findings.
        """
        images = []

        for root, dirs, _ in os.walk(image_dir):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if not os.path.isdir(dir_path):
                    continue

                nested_image_name = os.path.basename(dir_path)
                self._check_version_subdirs(
                    dir_path, nested_image_name, source_name, images
                )

        return images

    def _check_version_subdirs(
        self,
        dir_path: str,
        nested_image_name: str,
        source_name: str,
        images: List[ImageInfo],
    ) -> None:
        """
        ## Check for version subdirectories in a directory.
        ### Args:
            dir_path: Path to the directory
            nested_image_name: Name of the nested image
            source_name: Source name for the images
            images: List to append discovered images
        ### Returns:
            None
        ### Notes:
            - This method checks for version subdirectories in a given directory.
            - It also checks for excluded media types and logs the findings.
        """
        for subitem in os.listdir(dir_path):
            subdir_path = os.path.join(dir_path, subitem)
            if not os.path.isdir(subdir_path):
                continue

            image_version = subitem
            is_excluded = check_mediatype(subdir_path, self.excluded_mediatypes)

            logging.info(
                "Found nested version: %s:%s", nested_image_name, image_version
            )

            images.append(
                ImageInfo(
                    name=f"{source_name}:{nested_image_name}",
                    version=image_version,
                    path=subdir_path,
                    source=source_name,
                    excluded=is_excluded,
                )
            )

    def _scan_images(self, images: List[ImageInfo], convert_dir: pathlib.Path) -> Dict:
        """
        ## Scan discovered images.
        ### Args:
            images: List of ImageInfo objects representing discovered images
            convert_dir: Path to the directory for converted images
        ### Returns:
            Dictionary with scan results
        ### Notes:
            - This method scans the discovered images and returns the results.
            - It handles both OCI and Docker formats.
        """
        results = {}

        for img in images:
            # Handle image based on exclusion status
            if not img.excluded:
                oci_path = convert_image_to_oci(
                    img.path, f"{convert_dir}/{img.name}_{img.version}"
                )
                target_path = oci_path
                target_type = "oci-dir"
            else:
                target_path = img.path
                target_type = "dir"

            # Setup scanner args
            output_filename = f"{img.name}_{img.version}"
            scanner_args = {
                "target": target_path,
                "target_type": target_type,
                "name": img.name,
                "version": img.version,
                "output_file": output_filename,
            }

            # Run scan
            result = SyftScanner().scan(target_path, scanner_args)
            results[f"{img.name}:{img.version}"] = result

        return results

    def _scan_single_vuln(self, sbom_path: str) -> Dict:
        """
        ## Scan a single SBOM for vulnerabilities.
        ### Args:
            sbom_path: Path to the SBOM file
        ### Returns:
            Dictionary with vulnerability scan results
        """
        if not os.path.exists(sbom_path):
            raise ValueError(f"SBOM file not found: {sbom_path}")

        scanner_args = {
            "target": sbom_path,
            "is_sbom": True,
            "output_file": self.inputs.get(
                "vuln_output_file",
                os.path.join(os.path.dirname(sbom_path), "vuln.json"),
            ),
        }

        logging.info("Scanning SBOM for vulnerabilities: %s", sbom_path)
        return GrypeScanner().scan(sbom_path, scanner_args)

    def _scan_multiple_vulns(self, sbom_results: Dict) -> Dict:
        """
        ## Scan multiple SBOMs for vulnerabilities.
        ### Args:
            sbom_results: Dictionary with SBOM scan results
        ### Returns:
            Dictionary with vulnerability scan results
        """
        results = {}

        for image_name, image_result in sbom_results.get("results", {}).items():
            sbom_path = image_result.get("sbom_path")
            if sbom_path and os.path.exists(sbom_path):
                results[image_name] = self._scan_single_vuln(sbom_path)

        return {
            "success": True,
            "scanned_images": list(results.keys()),
            "results": results,
        }
