# Create the bootstrap cluster

Per https://archive-docs.d2iq.com/dkp/konvoy/2.2/choose-infrastructure/pre-provisioned/bootstrap/

```
cd /var/d2iq/dkp-v2.2.2
./dkp create bootstrap
```

Success looks like:
```
$ kubectl get po -A
NAMESPACE                           NAME                                                             READY
capa-system                         capa-controller-manager-74fffb5676-rxh25                         1/1
capi-kubeadm-bootstrap-system       capi-kubeadm-bootstrap-controller-manager-f5b45889c-d92bj        1/1
capi-kubeadm-control-plane-system   capi-kubeadm-control-plane-controller-manager-7dd6748f84-wvvxs   1/1
capi-system                         capi-controller-manager-8555dbbbfc-vkltj                         1/1
cappp-system                        cappp-controller-manager-5f5bb6956d-q274j                        1/1
capv-system                         capv-controller-manager-7bf4d8b66-45t42                          1/1
capz-system                         capz-controller-manager-7755865f5-n4f2l                          1/1
cert-manager                        cert-manager-848f547974-pbmxb                                    1/1
cert-manager                        cert-manager-cainjector-54f4cc6b5-rjx6x                          1/1
cert-manager                        cert-manager-webhook-7c9588c76-kwp94                             1/1
kube-system                         coredns-78fcd69978-gxqqb                                         1/1
kube-system                         coredns-78fcd69978-wh8ww                                         1/1
kube-system                         etcd-konvoy-capi-bootstrapper-control-plane                      1/1
kube-system                         kindnet-cgz6d                                                    1/1
kube-system                         kube-apiserver-konvoy-capi-bootstrapper-control-plane            1/1
kube-system                         kube-controller-manager-konvoy-capi-bootstrapper-control-plane   1/1
kube-system                         kube-proxy-6wdlz                                                 1/1
kube-system                         kube-scheduler-konvoy-capi-bootstrapper-control-plane            1/1

```