# Create the cluster

Per: https://archive-docs.d2iq.com/dkp/konvoy/2.2/choose-infrastructure/pre-provisioned/create-cluster/

**Context: Bootstrap VM**

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
  --control-plane-endpoint-host $d2iq_cp1_dns_name\
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

## Failure

Observe `KIBFailed`. The process never progresses past here.

```
$ ./dkp describe cluster --cluster-name $CLUSTER_NAME
NAME                                                         READY  SEVERITY  REASON                           SINCE  MESSAGE                                                      
Cluster/d2iq-poc                                             False  Warning   ScalingUp                        64s    Scaling up control plane to 3 replicas (actual 1)            
├─ClusterInfrastructure - PreprovisionedCluster/d2iq-poc                                                                                                                           
├─ControlPlane - KubeadmControlPlane/d2iq-poc-control-plane  False  Warning   ScalingUp                        64s    Scaling up control plane to 3 replicas (actual 1)            
│ └─Machine/d2iq-poc-control-plane-khvw2                     False  Warning   KIBFailed                        39s    1 of 2 completed                                             
└─Workers                                                                                                                                                                          
  └─MachineDeployment/d2iq-poc-md-0                          False  Warning   WaitingForAvailableMachines      70s    Minimum availability requires 3 replicas, current 0 available
    ├─Machine/d2iq-poc-md-0-745878dd89-4n8ln                 False  Info      WaitingForControlPlaneAvailable  70s    0 of 2 completed                                             
    ├─Machine/d2iq-poc-md-0-745878dd89-dtnhl                 False  Info      WaitingForControlPlaneAvailable  70s    0 of 2 completed                                             
    ├─Machine/d2iq-poc-md-0-745878dd89-k5m8s                 False  Info      WaitingForControlPlaneAvailable  70s    0 of 2 completed                                             
    └─Machine/d2iq-poc-md-0-745878dd89-p7wt2                 False  Info      WaitingForControlPlaneAvailable  70s    0 of 2 completed                                             
-bash-4.2$ 
```
