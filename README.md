# sbom

## Notes 

During the artesca scan, we use 25GB of storage. 

## ToDo

@m4nch0t:
- finish action.yml
- npm create different reuslt files foer dev package lock
- possibility to scan component with version (ex: artesca 2.1.0 need ZENKO_VERSION=2.8.13, so clone all zenko repos for this version)
- improve scan time with updated trivy db in image
- errors with skopeo:
  - Converting kube-rbac-proxy v0.14.1 from artesca-base
      time="2024-01-29T14:40:20Z" level=fatal msg="determining manifest MIME type for dir://imported_image: read /imported_image/manifest.json: input/output error"
  - Converting postgresql-exporter v0.12.0 from artesca-base
      time="2024-01-29T14:40:22Z" level=fatal msg="determining manifest MIME type for dir://imported_image: read /imported_image/manifest.json: input/output error"
  - Converting postgres-operator v1.10.0 from artesca-base
      time="2024-01-29T14:40:24Z" level=fatal msg="determining manifest MIME type for dir://imported_image: read /imported_image/manifest.json: input/output error"
  - Converting spilo-15 3.0-p1 from artesca-base
      time="2024-01-29T14:40:26Z" level=fatal msg="determining manifest MIME type for dir://imported_image: read /imported_image/manifest.json: input/output error"
  - Converting syslog 0.3.0 from artesca-base
      time="2024-01-29T14:40:32Z" level=fatal msg="determining manifest MIME type for dir://imported_image: read /imported_image/manifest.json: input/output error"
- errors on trivy scan for :
  - time="2024-01-29T14:50:51Z" level=fatal msg="creating an updated image manifest: unsupported image-specific operation on artifact with type \"application/vnd.unknown.config.v1+json\""
      Scanning backbeat-dashboards 8.6.29 from zenko
      2024-01-29T14:50:52.938Z        INFO    "--format cyclonedx" disables security scanning. Specify "--scanners vuln" explicitly if you want to include vulnerabilities in the CycloneDX report.
      2024-01-29T14:50:52.983Z        FATAL   image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
            * unable to open /images/zenko_backbeat-dashboards_8.6.29 as a Docker image: read /images/zenko_backbeat-dashboards_8.6.29: is a directory
            * unable to open /images/zenko_backbeat-dashboards_8.6.29 as an OCI Image: stat /images/zenko_backbeat-dashboards_8.6.29/index.json: no such file or directory
  - time="2024-01-29T14:50:53Z" level=fatal msg="creating an updated image manifest: unsupported image-specific operation on artifact with type \"application/vnd.unknown.config.v1+json\""
      Scanning backbeat-policies 8.6.29 from zenko
      2024-01-29T14:50:54.742Z        INFO    "--format cyclonedx" disables security scanning. Specify "--scanners vuln" explicitly if you want to include vulnerabilities in the CycloneDX report.
      2024-01-29T14:50:54.791Z        FATAL   image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
            * unable to open /images/zenko_backbeat-policies_8.6.29 as a Docker image: read /images/zenko_backbeat-policies_8.6.29: is a directory
            * unable to open /images/zenko_backbeat-policies_8.6.29 as an OCI Image: stat /images/zenko_backbeat-policies_8.6.29/index.json: no such file or directory
  - time="2024-01-29T14:52:58Z" level=fatal msg="creating an updated image manifest: unsupported image-specific operation on artifact with type \"application/vnd.oci.empty.v1+json\""
      Scanning cloudserver-dashboards 8.8.4 from zenko
      2024-01-29T14:52:59.975Z        INFO    "--format cyclonedx" disables security scanning. Specify "--scanners vuln" explicitly if you want to include vulnerabilities in the CycloneDX report.
      2024-01-29T14:53:00.010Z        FATAL   image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
            * unable to open /images/zenko_cloudserver-dashboards_8.8.4 as a Docker image: read /images/zenko_cloudserver-dashboards_8.8.4: is a directory
            * unable to open /images/zenko_cloudserver-dashboards_8.8.4 as an OCI Image: stat /images/zenko_cloudserver-dashboards_8.8.4/index.json: no such file or directory
  - time="2024-01-29T15:01:04Z" level=fatal msg="creating an updated image manifest: Unknown media type during manifest conversion: \"application/grafana-dashboard+json\""
      Scanning kafka-connect-dashboard 2.8.13 from zenko
      2024-01-29T15:01:05.282Z        INFO    "--format cyclonedx" disables security scanning. Specify "--scanners vuln" explicitly if you want to include vulnerabilities in the CycloneDX report.
      2024-01-29T15:01:05.318Z        FATAL   image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
            * unable to open /images/zenko_kafka-connect-dashboard_2.8.13 as a Docker image: read /images/zenko_kafka-connect-dashboard_2.8.13: is a directory
            * unable to open /images/zenko_kafka-connect-dashboard_2.8.13 as an OCI Image: stat /images/zenko_kafka-connect-dashboard_2.8.13/index.json: no such file or directory
  - time="2024-01-29T15:01:06Z" level=fatal msg="creating an updated image manifest: Unknown media type during manifest conversion: \"application/grafana-dashboard+json\""
      Scanning kafka-dashboard 2.8.13 from zenko
      2024-01-29T15:01:06.980Z        INFO    "--format cyclonedx" disables security scanning. Specify "--scanners vuln" explicitly if you want to include vulnerabilities in the CycloneDX report.
      2024-01-29T15:01:07.016Z        FATAL   image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
            * unable to open /images/zenko_kafka-dashboard_2.8.13 as a Docker image: read /images/zenko_kafka-dashboard_2.8.13: is a directory
            * unable to open /images/zenko_kafka-dashboard_2.8.13 as an OCI Image: stat /images/zenko_kafka-dashboard_2.8.13/index.json: no such file or directory
  - time="2024-01-29T15:03:02Z" level=fatal msg="creating an updated image manifest: Unknown media type during manifest conversion: \"application/grafana-dashboard+json\""
      Scanning mongodb-dashboard 2.8.13 from zenko
      2024-01-29T15:03:03.726Z        INFO    "--format cyclonedx" disables security scanning. Specify "--scanners vuln" explicitly if you want to include vulnerabilities in the CycloneDX report.
      2024-01-29T15:03:03.756Z        FATAL   image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
            * unable to open /images/zenko_mongodb-dashboard_2.8.13 as a Docker image: read /images/zenko_mongodb-dashboard_2.8.13: is a directory
            * unable to open /images/zenko_mongodb-dashboard_2.8.13 as an OCI Image: stat /images/zenko_mongodb-dashboard_2.8.13/index.json: no such file or directory
  - time="2024-01-29T15:03:10Z" level=fatal msg="creating an updated image manifest: Unknown media type during manifest conversion: \"application/grafana-dashboard+json\""
      Scanning redis-dashboard 2.8.13 from zenko
      2024-01-29T15:03:12.012Z        INFO    "--format cyclonedx" disables security scanning. Specify "--scanners vuln" explicitly if you want to include vulnerabilities in the CycloneDX report.
      2024-01-29T15:03:12.059Z        FATAL   image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
            * unable to open /images/zenko_redis-dashboard_2.8.13 as a Docker image: read /images/zenko_redis-dashboard_2.8.13: is a directory
            * unable to open /images/zenko_redis-dashboard_2.8.13 as an OCI Image: stat /images/zenko_redis-dashboard_2.8.13/index.json: no such file or directory
  - time="2024-01-29T15:03:19Z" level=fatal msg="creating an updated image manifest: unsupported image-specific operation on artifact with type \"application/vnd.oci.empty.v1+json\""
      Scanning s3utils-dashboards 1.14.3 from zenko
      2024-01-29T15:03:20.261Z        INFO    "--format cyclonedx" disables security scanning. Specify "--scanners vuln" explicitly if you want to include vulnerabilities in the CycloneDX report.
      2024-01-29T15:03:20.304Z        FATAL   image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
            * unable to open /images/zenko_s3utils-dashboards_1.14.3 as a Docker image: read /images/zenko_s3utils-dashboards_1.14.3: is a directory
            * unable to open /images/zenko_s3utils-dashboards_1.14.3 as an OCI Image: stat /images/zenko_s3utils-dashboards_1.14.3/index.json: no such file or directory
  - time="2024-01-29T15:03:22Z" level=fatal msg="creating an updated image manifest: unsupported image-specific operation on artifact with type \"application/vnd.unknown.config.v1+json\""
      Scanning sorbet-policies v1.1.1 from zenko
      2024-01-29T15:03:23.870Z        INFO    "--format cyclonedx" disables security scanning. Specify "--scanners vuln" explicitly if you want to include vulnerabilities in the CycloneDX report.
      2024-01-29T15:03:23.914Z        FATAL   image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
            * unable to open /images/zenko_sorbet-policies_v1.1.1 as a Docker image: read /images/zenko_sorbet-policies_v1.1.1: is a directory
            * unable to open /images/zenko_sorbet-policies_v1.1.1 as an OCI Image: stat /images/zenko_sorbet-policies_v1.1.1/index.json: no such file or directory
  - time="2024-01-29T15:05:20Z" level=fatal msg="creating an updated image manifest: unsupported image-specific operation on artifact with type \"application/vnd.unknown.config.v1+json\""
      Scanning vault-dashboards 8.8.1 from zenko
      2024-01-29T15:05:21.953Z        INFO    "--format cyclonedx" disables security scanning. Specify "--scanners vuln" explicitly if you want to include vulnerabilities in the CycloneDX report.
      2024-01-29T15:05:21.991Z        FATAL   image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
            * unable to open /images/zenko_vault-dashboards_8.8.1 as a Docker image: read /images/zenko_vault-dashboards_8.8.1: is a directory
            * unable to open /images/zenko_vault-dashboards_8.8.1 as an OCI Image: stat /images/zenko_vault-dashboards_8.8.1/index.json: no such file or directory
  - time="2024-01-29T15:05:22Z" level=fatal msg="creating an updated image manifest: unsupported image-specific operation on artifact with type \"application/vnd.unknown.config.v1+json\""
      Scanning vault-policies 8.8.1 from zenko
      2024-01-29T15:05:23.841Z        INFO    "--format cyclonedx" disables security scanning. Specify "--scanners vuln" explicitly if you want to include vulnerabilities in the CycloneDX report.
      2024-01-29T15:05:23.850Z        FATAL   image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
            * unable to open /images/zenko_vault-policies_8.8.1 as a Docker image: read /images/zenko_vault-policies_8.8.1: is a directory
        * unable to open /images/zenko_vault-policies_8.8.1 as an OCI Image: stat /images/zenko_vault-policies_8.8.1/index.json: no such file or directory
  - time="2024-01-29T15:05:30Z" level=fatal msg="creating an updated image manifest: unsupported image-specific operation on artifact with type \"application/vnd.unknown.config.v1+json\""
      Scanning zenko-ui-config 2.1.6 from zenko
      2024-01-29T15:05:31.755Z        INFO    "--format cyclonedx" disables security scanning. Specify "--scanners vuln" explicitly if you want to include vulnerabilities in the CycloneDX report.
      2024-01-29T15:05:31.803Z        FATAL   image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
            * unable to open /images/zenko_zenko-ui-config_2.1.6 as a Docker image: read /images/zenko_zenko-ui-config_2.1.6: is a directory
            * unable to open /images/zenko_zenko-ui-config_2.1.6 as an OCI Image: stat /images/zenko_zenko-ui-config_2.1.6/index.json: no such file or directory
  - time="2024-01-29T15:07:41Z" level=fatal msg="creating an updated image manifest: Unknown media type during manifest conversion: \"application/grafana-dashboard+json\""
      Scanning zookeeper-dashboard 2.8.13 from zenko
      2024-01-29T15:07:42.189Z        INFO    "--format cyclonedx" disables security scanning. Specify "--scanners vuln" explicitly if you want to include vulnerabilities in the CycloneDX report.
      2024-01-29T15:07:42.226Z        FATAL   image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
            * unable to open /images/zenko_zookeeper-dashboard_2.8.13 as a Docker image: read /images/zenko_zookeeper-dashboard_2.8.13: is a directory
            * unable to open /images/zenko_zookeeper-dashboard_2.8.13 as an OCI Image: stat /images/zenko_zookeeper-dashboard_2.8.13/index.json: no such file or directory
