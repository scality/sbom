# sbom

## Notes 

During the artesca scan, we use 25GB of storage. 

## ToDo

@m4nch0t:
- little bug with artifacts/repo/metalk8s/images/metalk8s-alert-logger/go.mod, skipped because he as a different format
- migrate code to python for modularity and cross project (artesca, zenko, ring, etc...)
- clean image scanning 
- add possibility to clone repo with specific version
- finish action.yml
- possibility to scan component with version (ex: artesca 2.1.0 need ZENKO_VERSION=2.8.13, so clone all zenko repos for this version)
- maybe a more customized skopeo image
- improve scan time with updated trivy db in image
- errors on trivy scan for :
  - image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
          * unable to open /images/zenko_backbeat-policies_8.6.29 as a Docker image: read /images/zenko_backbeat-policies_8.6.29: is a directory
          * unable to open /images/zenko_backbeat-policies_8.6.29 as an OCI Image: stat /images/zenko_backbeat-policies_8.6.29/index.json: no such file or directory
  - image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
          * unable to open /images/zenko_backbeat-dashboards_8.6.29 as a Docker image: read /images/zenko_backbeat-dashboards_8.6.29: is a directory
          * unable to open /images/zenko_backbeat-dashboards_8.6.29 as an OCI Image: stat /images/zenko_backbeat-dashboards_8.6.29/index.json: no such file or director
  - image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
          * unable to open /images/zenko_cloudserver-dashboards_8.8.4 as a Docker image: read /images/zenko_cloudserver-dashboards_8.8.4: is a directory
          * unable to open /images/zenko_cloudserver-dashboards_8.8.4 as an OCI Image: stat /images/zenko_cloudserver-dashboards_8.8.4/index.json: no such file or directory
  - image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
        * unable to open /images/zenko_kafka-connect-dashboard_2.8.13 as a Docker image: read /images/zenko_kafka-connect-dashboard_2.8.13: is a directory
        * unable to open /images/zenko_kafka-connect-dashboard_2.8.13 as an OCI Image: stat /images/zenko_kafka-connect-dashboard_2.8.13/index.json: no such file or directory
  - image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
        * unable to open /images/zenko_kafka-dashboard_2.8.13 as a Docker image: read /images/zenko_kafka-dashboard_2.8.13: is a directory
        * unable to open /images/zenko_kafka-dashboard_2.8.13 as an OCI Image: stat /images/zenko_kafka-dashboard_2.8.13/index.json: no such file or directory
  - image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
        * unable to open /images/zenko_mongodb-dashboard_2.8.13 as a Docker image: read /images/zenko_mongodb-dashboard_2.8.13: is a directory
        * unable to open /images/zenko_mongodb-dashboard_2.8.13 as an OCI Image: stat /images/zenko_mongodb-dashboard_2.8.13/index.json: no such file or directory
  - image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
        * unable to open /images/zenko_redis-dashboard_2.8.13 as a Docker image: read /images/zenko_redis-dashboard_2.8.13: is a directory
        * unable to open /images/zenko_redis-dashboard_2.8.13 as an OCI Image: stat /images/zenko_redis-dashboard_2.8.13/index.json: no such file or directory
  - image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
        * unable to open /images/zenko_s3utils-dashboards_1.14.3 as a Docker image: read /images/zenko_s3utils-dashboards_1.14.3: is a directory
        * unable to open /images/zenko_s3utils-dashboards_1.14.3 as an OCI Image: stat /images/zenko_s3utils-dashboards_1.14.3/index.json: no such file or directory
  - image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
        * unable to open /images/zenko_sorbet-policies_v1.1.1 as a Docker image: read /images/zenko_sorbet-policies_v1.1.1: is a directory
        * unable to open /images/zenko_sorbet-policies_v1.1.1 as an OCI Image: stat /images/zenko_sorbet-policies_v1.1.1/index.json: no such file or directory
  - image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
        * unable to open /images/zenko_vault-dashboards_8.8.1 as a Docker image: read /images/zenko_vault-dashboards_8.8.1: is a directory
        * unable to open /images/zenko_vault-dashboards_8.8.1 as an OCI Image: stat /images/zenko_vault-dashboards_8.8.1/index.json: no such file or directory
  - image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
        * unable to open /images/zenko_vault-policies_8.8.1 as a Docker image: read /images/zenko_vault-policies_8.8.1: is a directory
        * unable to open /images/zenko_vault-policies_8.8.1 as an OCI Image: stat /images/zenko_vault-policies_8.8.1/index.json: no such file or directory
  - image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
        * unable to open /images/zenko_zookeeper-dashboard_2.8.13 as a Docker image: read /images/zenko_zookeeper-dashboard_2.8.13: is a directory
        * unable to open /images/zenko_zookeeper-dashboard_2.8.13 as an OCI Image: stat /images/zenko_zookeeper-dashboard_2.8.13/index.json: no such file or directory
image scan error: scan error: unable to initialize a scanner: unable to initialize the archive scanner: 2 errors occurred:
        * unable to open /images/zenko_zenko-ui-config_2.1.6 as a Docker image: read /images/zenko_zenko-ui-config_2.1.6: is a directory
        * unable to open /images/zenko_zenko-ui-config_2.1.6 as an OCI Image: stat /images/zenko_zenko-ui-config_2.1.6/index.json: no such file or directory

