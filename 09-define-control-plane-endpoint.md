# Define control plane endpoint

No action here - not using a load balancer.

For now we will use the control plane VM 1 public DNS name as the single cluster endpoint address.

```
$ echo $d2iq_cp1_dns_name
ec2-54-157-10-215.compute-1.amazonaws.com
```