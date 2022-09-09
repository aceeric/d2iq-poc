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

> TODO when the **control plane** is behind a load balancer add the control plane load balancer DNS and and IP to the `--extra-sans` parameter

Specify the internal IP of control plane VM 1 for the control plane end point: `$d2iq_cp1`. No override secret is specified. Note - the timeout below is notional for an extremely slow environment:
```
./dkp create cluster preprovisioned\
  --cluster-name $CLUSTER_NAME\
  --extra-sans $d2iq_cp1_private_dns_name,$d2iq_cp2_private_dns_name,$d2iq_cp3_private_dns_name,$d2iq_cp1,$d2iq_cp2,$d2iq_cp3\
  --control-plane-endpoint-host $d2iq_cp1\
  --control-plane-replicas 3\
  --worker-replicas 3\
  --registry-mirror-url $DOCKER_REGISTRY_URL\
  --registry-mirror-cacert $DOCKER_REGISTRY_CA\
  --timeout=60m
```

## Monitor
```
kubectl -n cappp-system logs deploy/cappp-controller-manager --timestamps -f
```

And:
```
watch ./dkp describe cluster --cluster-name $CLUSTER_NAME
```

## Troubleshooting

If the `describe cluster` command shows any of the nodes as `KIBFailed`, look for failed jobs (max retries exceeded) and delete those jobs. They will be re-generated and retried. Eventually, the process should complete. The jobs appear to be sensitive to slow VMs.

## Wait for completion
```
kubectl wait --for=condition=ControlPlaneReady clusters/$CLUSTER_NAME --timeout=30m
```

Success result:
```
cluster.cluster.x-k8s.io/d2iq-poc condition met
```

## Success looks like:
```
./dkp describe cluster --cluster-name $CLUSTER_NAME
```

Output:
```
NAME                                                         READY  SEVERITY  REASON  SINCE  MESSAGE
Cluster/d2iq-poc                                             True                     40s
├─ClusterInfrastructure - PreprovisionedCluster/d2iq-poc
├─ControlPlane - KubeadmControlPlane/d2iq-poc-control-plane  True                     40s
│ ├─Machine/d2iq-poc-control-plane-fkq6l                     True                     38m
│ ├─Machine/d2iq-poc-control-plane-lfvlx                     True                     20m
│ └─Machine/d2iq-poc-control-plane-t9jvp                     True                     41s
└─Workers
  └─MachineDeployment/d2iq-poc-md-0                          True                     16m
    ├─Machine/d2iq-poc-md-0-745878dd89-5c9w4                 True                     6m44s
    ├─Machine/d2iq-poc-md-0-745878dd89-6dxcw                 True                     17m
    └─Machine/d2iq-poc-md-0-745878dd89-sgvdk                 True                     18m
```

## Get the new cluster kubeconfig

```
./dkp get kubeconfig -c $CLUSTER_NAME > ~/.kube/$CLUSTER_NAME.conf
```

## List pods in the new cluster
```
kubectl --kubeconfig ~/.kube/$CLUSTER_NAME.conf get po -A
```

Result:
```
NAMESPACE                NAME                                                    READY   STATUS
calico-system            calico-kube-controllers-57fbd7bd59-vncmx                1/1     Running
calico-system            calico-node-4dbdt                                       1/1     Running
calico-system            calico-node-6lcbc                                       1/1     Running
calico-system            calico-node-6m4fg                                       1/1     Running
calico-system            calico-node-mr54t                                       1/1     Running
calico-system            calico-node-svwgj                                       1/1     Running
calico-system            calico-node-zs5gm                                       1/1     Running
calico-system            calico-typha-dd666cf88-6xdzk                            1/1     Running
calico-system            calico-typha-dd666cf88-jxkr5                            1/1     Running
calico-system            calico-typha-dd666cf88-wfl7q                            1/1     Running
kube-system              coredns-78fcd69978-2hn8r                                1/1     Running
kube-system              coredns-78fcd69978-kfjwv                                1/1     Running
kube-system              etcd-ip-10-114-148-19.evoforge.org                      1/1     Running
kube-system              etcd-ip-10-114-148-22.evoforge.org                      1/1     Running
kube-system              etcd-ip-10-114-148-44.evoforge.org                      1/1     Running
kube-system              kube-apiserver-ip-10-114-148-19.evoforge.org            1/1     Running
kube-system              kube-apiserver-ip-10-114-148-22.evoforge.org            1/1     Running
kube-system              kube-apiserver-ip-10-114-148-44.evoforge.org            1/1     Running
kube-system              kube-controller-manager-ip-10-114-148-19.evoforge.org   1/1     Running
kube-system              kube-controller-manager-ip-10-114-148-22.evoforge.org   1/1     Running
kube-system              kube-controller-manager-ip-10-114-148-44.evoforge.org   1/1     Running
kube-system              kube-proxy-bj2bs                                        1/1     Running
kube-system              kube-proxy-g7gkx                                        1/1     Running
kube-system              kube-proxy-j6dzh                                        1/1     Running
kube-system              kube-proxy-lkx7h                                        1/1     Running
kube-system              kube-proxy-tkg5m                                        1/1     Running
kube-system              kube-proxy-xdh2q                                        1/1     Running
kube-system              kube-scheduler-ip-10-114-148-19.evoforge.org            1/1     Running
kube-system              kube-scheduler-ip-10-114-148-22.evoforge.org            1/1     Running
kube-system              kube-scheduler-ip-10-114-148-44.evoforge.org            1/1     Running
kube-system              local-volume-provisioner-4r5d7                          1/1     Running
kube-system              local-volume-provisioner-bmglp                          1/1     Running
kube-system              local-volume-provisioner-dkbr6                          1/1     Running
kube-system              local-volume-provisioner-jc4bj                          1/1     Running
kube-system              local-volume-provisioner-p22zk                          1/1     Running
kube-system              local-volume-provisioner-q2tff                          1/1     Running
metallb-system           controller-567fb5f8dd-txdns                             1/1     Running
metallb-system           speaker-58f5t                                           1/1     Running
metallb-system           speaker-7qlcg                                           1/1     Running
metallb-system           speaker-kqmx2                                           1/1     Running
metallb-system           speaker-lpl2v                                           1/1     Running
metallb-system           speaker-nsn8j                                           1/1     Running
metallb-system           speaker-xfjhn                                           1/1     Running
node-feature-discovery   node-feature-discovery-master-84c67dcbb6-dx2dq          1/1     Running
node-feature-discovery   node-feature-discovery-worker-l62mw                     1/1     Running
node-feature-discovery   node-feature-discovery-worker-n595l                     1/1     Running
node-feature-discovery   node-feature-discovery-worker-njbpm                     1/1     Running
tigera-operator          tigera-operator-d499f5c8f-jmjw2                         1/1     Running
```

## Delete the cluster

At some future point you can delete the downstream cluster from the bootstrap cluster. This variant does not actually remove the downstream cluster - the the resources from the bootstrap cluster.
```
./dkp delete cluster --cluster-name $CLUSTER_NAME --delete-kubernetes-resources=false
```