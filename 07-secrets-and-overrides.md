# Create secrets and overrides

Based on: https://archive-docs.d2iq.com/dkp/konvoy/2.2/choose-infrastructure/pre-provisioned/create-secrets-and-overrides/

**Context: Bootstrap VM**

## Cluster name
```
export CLUSTER_NAME=d2iq-poc
```

## SSH Secret
```
export SSH_PRIVATE_KEY_FILE=~/.ssh/d2iq
export SSH_PRIVATE_KEY_SECRET_NAME=$CLUSTER_NAME-ssh-key
kubectl create secret generic ${SSH_PRIVATE_KEY_SECRET_NAME} --from-file=ssh-privatekey=${SSH_PRIVATE_KEY_FILE}
kubectl label secret ${SSH_PRIVATE_KEY_SECRET_NAME} clusterctl.cluster.x-k8s.io/move=
```

## Overrides
```
kubectl create secret generic $CLUSTER_NAME-user-overrides --from-file=overrides.yaml=./kib/overrides/offline.yaml
kubectl label secret $CLUSTER_NAME-user-overrides clusterctl.cluster.x-k8s.io/move=
```