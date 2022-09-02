# Install Kommander

Per: https://archive-docs.d2iq.com/dkp/kommander/2.2/install/air-gapped/

**Context: Bootstrap VM**

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

## TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO

Hand-patched the manifest:
```
  traefik:
    enabled: true
    values: |
      service:
        annotations:
          service.beta.kubernetes.io/aws-load-balancer-internal: "false" <<<<<<<< HAND JAM!!!!!!
```

traefik times out - helm elease needs to be deleted and then dkp re-run


STILL DOWN: PATRICK SAYS:

It needs an LB ingress, this is a type of ingress associated with additional infrastructure in K8s. we mimic the cloud native functionality with MetalLB when we don't have another option. I.E. fully on baremetal servers.
So for AWS even airgapped preprovsioned we can do that but that is not a standard supported/tested config so those docs  are not on our website
Similarly the Traefik in nodeport mode doesn't work smoothly because we have a lot of UI and suchs API like Dex that get checked for routing so if the traefik doesn't get a URL it has no route to check, the URL comes form the LB type K8s service.
let me dig up the old docs we have for 1.8 adn update them to 2.x for you for Tuesday on how to config AWS preprovsioned for AWS K8s operations .
For Openstack you will still need a routable VIP for MetalLB and with a DNS URL we can do the routing and then shove a proper LB in between UIs and K8s MelaLB VP.
Infinite configurations infinite complexities to adjust for.



VERIFY STEPS HERE: https://archive-docs.d2iq.com/dkp/kommander/2.2/install/networked/#verify-installation


















## Verify

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


