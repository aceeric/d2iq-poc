# Create the cluster

Per: https://archive-docs.d2iq.com/dkp/konvoy/2.2/choose-infrastructure/pre-provisioned/create-cluster/


## Directory context
```
cd /var/d2iq/dkp-v2.2.2
```

## Define environment variables
```
export CLUSTER_NAME=d2iq-poc
export DOCKER_REGISTRY_URL=https://$(hostname):5000
export DOCKER_REGISTRY_CA=~/pki/ca.pem
```

## Create the downstream cluster
```
./dkp create cluster preprovisioned\
  --cluster-name $CLUSTER_NAME\
  --control-plane-endpoint-host ip-10-114-148-19.evoforge.org\
  --override-secret-name $CLUSTER_NAME-user-overrides\
  --registry-mirror-url $DOCKER_REGISTRY_URL\
  --registry-mirror-cacert $DOCKER_REGISTRY_CA
```

## Monitor
```
watch ./dkp describe cluster --cluster-name $CLUSTER_NAME
```

And:
```
kubectl -n cappp-system logs deploy/cappp-controller-manager --timestamps -f
```
