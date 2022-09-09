# Install Kommander

Per: https://archive-docs.d2iq.com/dkp/kommander/2.2/install/air-gapped/

**Context: Bootstrap VM**

All this will be done in the context of the new cluster:
```
export KUBECONFIG=~/.kube/d2iq-poc.conf
```

## Hack MetalLB

Create a MetalLB configuration that enables it to provision a Kubernetes `LoadBalancer` resource.
```
cat << EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  namespace: metallb-system
  name: config
data:
  config: |
    address-pools:
    - name: default
      protocol: layer2
      addresses:
      - $d2iq_w1/32
EOF
```

## Directory context
```
cd /var/d2iq/dkp-v2.2.2
```

## Extract files

These image bundles are gzips inside TAR files. So the gzips have to be extracted from the TAR files before they can be used. Different gzips are used for different purposes.

```
mkdir /var/tmp/bundles

tar -xvf dkp-kommander-charts-bundle-v2.2.2.tar.gz -C /var/tmp/bundles
tar -xvf dkp-insights-image-bundle-v2.2.2.tar.gz -C /var/tmp/bundles
tar -xvf dkp-insights-charts-bundle-v2.2.2.tar.gz -C /var/tmp/bundles
tar -xvf dkp-catalog-applications-image-bundle-v2.2.2.tar.gz -C /var/tmp/bundles
tar -xvf dkp-catalog-applications-charts-bundle-v2.2.2.tar.gz -C /var/tmp/bundles
tar -xvf kommander-image-bundle-v2.2.2.tar.gz -C /var/tmp/bundles
```

## Verify

File `NOTICES.txt` can be ignored.
```
$ ls -l /var/tmp/bundles | sort
-rw-rw-r-- 1 esace esace    1416899 Jul  7 20:31 dkp-kommander-charts-bundle-v2.2.2.tar.gz
-rw-rw-r-- 1 esace esace  198423141 Jul  7 21:20 dkp-insights-image-bundle-v2.2.2.tar.gz
-rw-rw-r-- 1 esace esace     342541 Jul  7 21:20 dkp-insights-charts-bundle-v2.2.2.tar.gz
-rw-rw-r-- 1 esace esace 3511281474 Jul  7 21:21 dkp-catalog-applications-image-bundle-v2.2.2.tar.gz
-rw-rw-r-- 1 esace esace     377633 Jul  7 21:21 dkp-catalog-applications-charts-bundle-v2.2.2.tar.gz
-rw-rw-r-- 1 esace esace 4278271504 Jul  7 21:08 kommander-image-bundle-v2.2.2.tar.gz
-rw-rw-r-- 1 esace esace         74 Jul  7 22:00 NOTICES.txt
```

## Load images to the private registry
```
./dkp push image-bundle\
  --image-bundle /var/tmp/bundles/kommander-image-bundle-v2.2.2.tar.gz\
  --to-registry $(hostname):5000

./dkp push image-bundle\
  --image-bundle /var/tmp/bundles/dkp-catalog-applications-image-bundle-v2.2.2.tar.gz\
  --to-registry $(hostname):5000

./dkp push image-bundle\
  --image-bundle /var/tmp/bundles/dkp-insights-image-bundle-v2.2.2.tar.gz\
  --to-registry $(hostname):5000
```

## Environment variables
```
export CLUSTER_NAME=d2iq-poc
```

## Create a directory for the kommander init file
```
mkdir ~/kommander
```

## Generate configuration file

We will subsequently use Kustomize to modify the manifest, so add a name to the manifest as required by Kustomize:
```
./dkp install kommander --init --airgapped >| ~/kommander/kommander-install.yaml &&\
  sed "s/kind: Installation/kind: Installation\nmetadata:\n  name: $CLUSTER_NAME/"\
  -i ~/kommander/kommander-install.yaml
```

## Create a kustomize patch file

See `files/kustomization.yaml`. Copy that file into the bootstrap VM now:

**Context: Dev Env**

```
scp -i d2iq files/kustomization.yaml ${USER#*\\}@$d2iq_bootstrap:./kommander/
```

## Create the patched kommander install file

**Context: Bootstrap VM**

This step uses kustomize to patch the kommander manifest. Before writing the patched manifest out, the metadata lines introduced above are removed because they break `dkp` at this version level.

```
kubectl kustomize ~/kommander | sed -e '/metadata:/,+2d' >| ~/kommander/kommander-install-patched.yaml
```

## HACK HACK HACK HACK HACK HACK HACK HACK HACK HACK

> JUST USE THIS KOMMANDER YAML FOR NOW
```
cat <<EOF >| ~/kommander/kommander-install-patched.yaml
ageEncryptionSecretName: sops-age
airgapped:
  enabled: true
apiVersion: config.kommander.mesosphere.io/v1alpha1
apps:
  dex:
    enabled: true
  dex-k8s-authenticator:
    enabled: true
  dkp-insights-management:
    enabled: true
  fluent-bit:
    enabled: false
  gatekeeper:
    enabled: false
  gitea:
    enabled: true
  grafana-logging:
    enabled: false
  grafana-loki:
    enabled: false
  kommander:
    enabled: true
  kube-prometheus-stack:
    enabled: true
    values: |
      prometheus:
        additionalServiceMonitors:
          - name: dkp-service-monitor-metrics-dex-controller
            selector:
              matchLabels:
                servicemonitor.kommander.mesosphere.io/path: "metrics"
                kubeaddons.mesosphere.io/name: "dex-controller"
            namespaceSelector:
              any: true
            endpoints:
              - port: https
                interval: 30s
                scheme: https
                bearerTokenFile: /var/run/secrets/kubernetes.io/serviceaccount/token
                tlsConfig:
                  caFile: "/etc/prometheus/secrets/dex/ca.crt"
                  certFile: "/etc/prometheus/secrets/dex/tls.crt"
                  keyFile: "/etc/prometheus/secrets/dex/tls.key"
                  insecureSkipVerify: true
          - name: dkp-service-monitor-metrics-thanos
            selector:
              matchLabels:
                servicemonitor.kommander.mesosphere.io/path: "metrics"
            namespaceSelector:
              matchNames:
                - kommander
                - kubecost
            endpoints:
              # Service port for Thanos Querier, running in Kommander.
              # If we ever add a Kommander-specific Prometheus, this
              # endpoint should be removed and added to that Prometheus's
              # configuration.
              - targetPort: 10902
                interval: 30s
          - name: dkp-service-monitor-metrics-centralized-grafana
            selector:
              matchLabels:
                app.kubernetes.io/instance: "centralized-grafana"
                servicemonitor.kommander.mesosphere.io/path: "metrics"
            namespaceSelector:
              matchNames:
                - kommander
            endpoints:
              - port: service
                interval: 30s
          - name: dkp-service-monitor-metrics-kommander
            selector:
              matchLabels:
                servicemonitor.kommander.mesosphere.io/path: "metrics"
                kommander.mesosphere.io/name: "kommander"
            namespaceSelector:
              matchNames:
                - kommander
            endpoints:
              - port: https
                interval: 30s
                scheme: https
                bearerTokenFile: /var/run/secrets/kubernetes.io/serviceaccount/token
                tlsConfig:
                  insecureSkipVerify: true
          - name: dkp-service-monitor-karma
            selector:
              matchLabels:
                servicemonitor.kommander.mesosphere.io/path: "dkp__kommander__monitoring__karma__metrics"
            namespaceSelector:
              matchNames:
                - kommander
            endpoints:
              - path: /dkp/kommander/monitoring/karma/metrics
                targetPort: http
                interval: 30s
          # Below service monitors are copied from kube-prometheus-stack-d2iq-defaults
          # This is because arrays in values are replaced, not appended.
          - name: dkp-service-monitor-metrics
            selector:
              matchLabels:
                servicemonitor.kommander.mesosphere.io/path: "metrics"
            namespaceSelector:
              any: true
            endpoints:
              - port: metrics
                interval: 30s
              - port: monitoring
                interval: 30s
              # Service port for external-dns
              - targetPort: 7979
                interval: 30s
          - name: dkp-service-monitor-metrics-http
            selector:
              matchLabels:
                servicemonitor.kommander.mesosphere.io/path: "metrics"
                servicemonitor.kommander.mesosphere.io/port: "http"
            namespaceSelector:
              any: true
            endpoints:
              # Service ports for loki-distributed
              - targetPort: http
                interval: 30s
          - name: dkp-service-monitor-api-v1-metrics-prometheus
            selector:
              matchLabels:
                servicemonitor.kommander.mesosphere.io/path: "api__v1__metrics__prometheus"
            namespaceSelector:
              any: true
            endpoints:
              - path: /api/v1/metrics/prometheus
                port: metrics
                interval: 30s
          - name: dkp-service-monitor-api-v1-metrics-prometheus-http-10s
            selector:
              matchLabels:
                servicemonitor.kommander.mesosphere.io/path: "api__v1__metrics__prometheus"
                servicemonitor.kommander.mesosphere.io/port: "http"
                servicemonitor.kommander.mesosphere.io/interval: "10s"
            namespaceSelector:
              any: true
            endpoints:
              - path: /api/v1/metrics/prometheus
                port: http
                interval: 10s
          - name: dkp-service-monitor-prometheus-metrics
            selector:
              matchLabels:
                servicemonitor.kommander.mesosphere.io/path: "prometheus__metrics"
            namespaceSelector:
              any: true
            endpoints:
              - path: /_prometheus/metrics
                targetPort: 5601
                interval: 30s
        prometheusSpec:
          secrets:
            - dex
          storageSpec:
            volumeClaimTemplate:
              spec:
                # 100Gi is the default size for the chart
                resources:
                  requests:
                    storage: 100Gi
          resources:
            limits:
              cpu: 2000m
              memory: 10922Mi
            requests:
              cpu: 1000m
              memory: 4000Mi
      grafana:
        resources:
          # keep request = limit to keep this container in guaranteed class
          limits:
            cpu: 300m
            memory: 100Mi
          requests:
            cpu: 200m
            memory: 100Mi
      alertmanager:
        alertmanagerSpec:
          resources:
            limits:
              cpu: 200m
              memory: 250Mi
            requests:
              cpu: 100m
              memory: 200Mi
  kubefed:
    enabled: true
  kubernetes-dashboard:
    enabled: true
  kubetunnel:
    enabled: false
  logging-operator:
    enabled: false
  minio-operator:
    enabled: false
  prometheus-adapter:
    enabled: true
  reloader:
    enabled: true
  traefik:
    enabled: true
  traefik-forward-auth-mgmt:
    enabled: true
  velero:
    enabled: false
catalog:
  repositories:
  - labels:
      kommander.d2iq.io/gitapps-gitrepository-type: dkp
      kommander.d2iq.io/workspace-default-catalog-repository: "true"
    name: insights-catalog-applications
    path: ./dkp-insights-v2.2.2.tar.gz
  - labels:
      kommander.d2iq.io/gitapps-gitrepository-type: dkp
      kommander.d2iq.io/project-default-catalog-repository: "true"
      kommander.d2iq.io/workspace-default-catalog-repository: "true"
    name: dkp-catalog-applications
    path: ./dkp-catalog-applications-v2.2.2.tar.gz
clusterHostname: ""
kind: Installation
EOF
```

## Verify preparatory steps

The D2IQ tarball that contains TARs ending with `.gz` which need to be untarred to explode `.tar.gz` files that are actually gzips is confusing. Take a moment to validate steps above. Your output should match:

### list the files that the Kommander install will use:
```
(
  ls -l  ~/kommander/kommander-install-patched.yaml
  ls -ld ./kommander-applications-v2.2.2
  ls -l  /var/tmp/bundles/dkp-kommander-charts-bundle-v2.2.2.tar.gz
  ls -l  /var/tmp/bundles/dkp-catalog-applications-charts-bundle-v2.2.2.tar.gz
  ls -l  /var/tmp/bundles/dkp-insights-charts-bundle-v2.2.2.tar.gz
  ls -l  ./dkp-insights-v2.2.2.tar.gz
  ls -l  ./dkp-catalog-applications-v2.2.2.tar.gz
) | sort | column -t
```

Should produce:
```
drwxrwxr-x 4 esace esace 36      Sep  1 16:51  ./kommander-applications-v2.2.2
-rw-rw-r-- 1 esace esace 1416899 Jul  7 20:31  /var/tmp/bundles/dkp-kommander-charts-bundle-v2.2.2.tar.gz
-rw-rw-r-- 1 esace esace 15299   Aug  9 11:53  ./dkp-catalog-applications-v2.2.2.tar.gz
-rw-rw-r-- 1 esace esace 342541  Jul  7 21:20  /var/tmp/bundles/dkp-insights-charts-bundle-v2.2.2.tar.gz
-rw-rw-r-- 1 esace esace 377633  Jul  7 21:21  /var/tmp/bundles/dkp-catalog-applications-charts-bundle-v2.2.2.tar.gz
-rw-rw-r-- 1 esace esace 7602    Aug  9 11:53  ./dkp-insights-v2.2.2.tar.gz
-rw-rw-r-- 1 esace esace 7715    Sep  2 13:49  /home/esace/kommander/kommander-install-patched.yaml
```

And validate the exloded Gzips. The following commands will produce no output if the GZips are valid:
```
gunzip -t /var/tmp/bundles/dkp-catalog-applications-charts-bundle-v2.2.2.tar.gz
gunzip -t /var/tmp/bundles/dkp-insights-charts-bundle-v2.2.2.tar.gz
gunzip -t /var/tmp/bundles/dkp-kommander-charts-bundle-v2.2.2.tar.gz
gunzip -t ./dkp-insights-v2.2.2.tar.gz
gunzip -t ./dkp-catalog-applications-v2.2.2.tar.gz
```

If everything looks correct, proceed to the next step.

## Install Kommander

> Note: The D2IQ documentation specifies a `.gz` for the `--kommander-applications-repository` option but the air-gapped tarball provided by D2IQ explodes that to a directory, so the command below uses directory `kommander-applications-v2.2.2` rather than file `kommander-applications-v2.2.2.tar.gz`.
```
./dkp install kommander\
  --kubeconfig ~/.kube/d2iq-poc.conf\
  --installer-config ~/kommander/kommander-install-patched.yaml\
  --kommander-applications-repository ./kommander-applications-v2.2.2\
  --charts-bundle /var/tmp/bundles/dkp-kommander-charts-bundle-v2.2.2.tar.gz\
  --charts-bundle /var/tmp/bundles/dkp-catalog-applications-charts-bundle-v2.2.2.tar.gz\
  --charts-bundle /var/tmp/bundles/dkp-insights-charts-bundle-v2.2.2.tar.gz
```

Success looks like:
```
 ✓ Ensuring applications repository fetcher is deployed
 ✓ Ensuring base resources are deployed
 ✓ Ensuring Flux is deployed 
 ✓ Ensuring Kommander Root CA is deployed 
 ✓ Ensuring Chartmuseum is deployed 
 ✓ Ensuring helm repository configuration is deployed 
 ✓ Ensuring ingress certificate is deployed
 ✓ Ensuring Gitea is deployed 
 ✓ Ensuring Application definitions are deployed 
 ✓ Ensuring Bootstrap repository is deployed 
 ✓ Ensuring Age encryption is deployed 
 ✓ Ensuring Flux configuration is deployed 
 ✓ Ensuring Gatekeeper is deployed
 ✓ Ensuring Kommander App Management is deployed 
 ✓ Ensuring core AppDeployments are deployed 
 ✓ Ensuring AppDeployments for configured Apps are deployed
 ✓ Ensuring Catalog Repository Loader is deployed 
```

## Verify
```
kubectl --kubeconfig ~/.kube/d2iq-poc.conf -n kommander wait --for condition=Released helmreleases --all --timeout 15m
```

> Wait a few mintutes for **all** the pods and services to be clean and running. There seems to be a few minutes of jitter in there...

## Deactivate MetalLB

```
kubectl -n metallb-system patch daemonset speaker\
  -p '{"spec": {"template": {"spec": {"nodeSelector": {"non-existing": "true"}}}}}'

kubectl -n metallb-system scale deploy controller --replicas=0
```

## Access the Kommander UI

Based on: https://archive-docs.d2iq.com/dkp/kommander/2.2/install/networked/#verify-installation

### Get the Kommander URL

```
kubectl -n kommander get svc kommander-traefik -o go-template='https://{{with index .status.loadBalancer.ingress 0}}{{or .hostname .ip}}{{end}}/dkp/kommander/dashboard{{ "\n"}}'
```

Example output:
```
https://10.114.174.22/dkp/kommander/dashboard
```

### Get the Admin credentials

```
kubectl -n kommander get secret dkp-credentials -o go-template='Username: {{.data.username|base64decode}}{{ "\n"}}Password: {{.data.password|base64decode}}{{ "\n"}}'
```

Example output:
```
Username: scintillating_potato
Password: 84SDLKSJDFwerfSDFsed54sSDFSDFeryujhfgh85dzgfDSFGDFG435345gsdf
```

### In the browser

Access the URL in the browser and provide the credentials to access the Kommander UI.
