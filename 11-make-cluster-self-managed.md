# Make cluster self-managed

Per: https://archive-docs.d2iq.com/dkp/konvoy/2.2/choose-infrastructure/pre-provisioned/create-cluster/

**Context: Bootstrap VM**

## Directory context
```
cd /var/d2iq/dkp-v2.2.2
```

## Environment variables
```
export CLUSTER_NAME=d2iq-poc
```

## Deploy cluster lifecycle services

Deploy cluster lifecycle services on the workload cluster:
```
./dkp create capi-components --kubeconfig ~/.kube/$CLUSTER_NAME.conf --timeout=30m
```

### Result
```
You are relying on the default value for flag '--with-aws-bootstrap-credentials', the current default 'true' will be changed to 'false' in a future release.
 ✓ Initializing new CAPI components 
```

## Move Cluster API objects

Move the Cluster API objects from the bootstrap to the workload cluster:
```
./dkp move capi-resources --to-kubeconfig ~/.kube/$CLUSTER_NAME.conf
```

Result:
```
 ✓ Moving cluster resources 
You can now view resources in the moved cluster by using the --kubeconfig flag with kubectl. For example: kubectl --kubeconfig=/home/esace/.kube/d2iq-poc.conf get nodes
```

## Wait for the downstream cluster

This uses the kube config exported from step `NN-create-the-cluster.md`:
```
kubectl --kubeconfig ~/.kube/$CLUSTER_NAME.conf wait\
  --for=condition=ControlPlaneReady clusters/$CLUSTER_NAME --timeout=20m
```

Result:
```
cluster.cluster.x-k8s.io/d2iq-poc condition met
```

## Describe the downstream management cluster:
```
./dkp describe cluster --cluster-name $CLUSTER_NAME --kubeconfig ~/.kube/$CLUSTER_NAME.conf
```

## Output
```
NAME                                                         READY  SEVERITY  REASON  SINCE  MESSAGE
Cluster/d2iq-poc                                             True                     17m           
├─ClusterInfrastructure - PreprovisionedCluster/d2iq-poc                                            
├─ControlPlane - KubeadmControlPlane/d2iq-poc-control-plane  True                     17m           
│ ├─Machine/d2iq-poc-control-plane-fkq6l                     True                     17m           
│ ├─Machine/d2iq-poc-control-plane-lfvlx                     True                     17m           
│ └─Machine/d2iq-poc-control-plane-t9jvp                     True                     17m           
└─Workers                                                                                           
  └─MachineDeployment/d2iq-poc-md-0                          True                     17m           
    ├─Machine/d2iq-poc-md-0-745878dd89-5c9w4                 True                     13s           
    ├─Machine/d2iq-poc-md-0-745878dd89-6dxcw                 True                     13s           
    └─Machine/d2iq-poc-md-0-745878dd89-sgvdk                 True                     13s           
```

## Remove the bootstrap cluster (optional)

You can remove the bootstrap cluster since the new downstream cluster now has all the CAPI management capability:

```
./dkp delete bootstrap 
```