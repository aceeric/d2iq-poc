# Provision VMs

**Context: Dev Env**

## Provision the VMS in public AWS

Run the script: `scripts/provision-vms`, and skip ahead to `Wait for VMs to be ready`.

## Provision the VMS in eVo
```
for vmname in d2iq-bootstrap d2iq-cp1 d2iq-cp2 d2iq-cp3 d2iq-w1 d2iq-w2 d2iq-w3; do
  ./scripts/provision-ec2-instance\
    --vol-size 200 \
    --ssh-keys $(pwd)/d2iq \
    --nowait \
    project-vpc \
    us-east-subnet-5 \
    devcraft-networking-SecurityGroup-Q6P991Z0L3X6 \
    eVo_AMI_CentOS7 \
    t3.xlarge \
    $vmname \
    evoforge-user || break
done
```

## Wait for VMs to be ready

Run `watch scripts/get-instance-status`. Once all the instances report `STATUS = ok`, proceed to the next step. E.g.:
```
INSTANCE_ID          STATUS
i-00661d437d277dd62  ok
i-00ca5701d534a5a04  ok
i-016769ce187994fa7  ok
i-0431368df5fd5ce00  ok
i-0afdd888284a74496  ok
i-0cb975388de4b1e70  ok
i-0d1b0ac7b79627cd4  ok
```

## Use this snippet to see the relevant VM info
```
aws ec2 describe-instances --filters "Name=tag:Name,Values=d2iq*"\
  --query "Reservations[*].Instances[*].{name: Tags[?Key=='Name'] | [0].Value, instance_id: InstanceId, private_ip: PrivateIpAddress, private_dns: PrivateDnsName, public_ip: PublicIpAddress, public_dns: PublicDnsName, state: State.Name}"\
  --output table
```

In the public AWS, the output should be like the following:
```
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
|                                                                           DescribeInstances                                                                           |
+---------------------+-----------------+--------------------------------+----------------+---------------------------------------------+----------------+--------------+
|     instance_id     |      name       |          private_dns           |  private_ip    |                 public_dns                  |   public_ip    |    state     |
+---------------------+-----------------+--------------------------------+----------------+---------------------------------------------+----------------+--------------+
|  i-0cb975388de4b1e70|  d2iq-w1        |  ip-172-31-23-222.ec2.internal |  172.31.23.222 |  ec2-54-91-101-122.compute-1.amazonaws.com  |  54.91.101.122 |  running     |
|  i-0d1b0ac7b79627cd4|  d2iq-cp2       |  ip-172-31-16-51.ec2.internal  |  172.31.16.51  |  ec2-54-83-92-172.compute-1.amazonaws.com   |  54.83.92.172  |  running     |
|  i-0afdd888284a74496|  d2iq-w2        |  ip-172-31-28-98.ec2.internal  |  172.31.28.98  |  ec2-54-226-101-241.compute-1.amazonaws.com |  54.226.101.241|  running     |
|  i-016769ce187994fa7|  d2iq-w3        |  ip-172-31-29-80.ec2.internal  |  172.31.29.80  |  ec2-54-90-155-110.compute-1.amazonaws.com  |  54.90.155.110 |  running     |
|  i-0431368df5fd5ce00|  d2iq-cp1       |  ip-172-31-16-12.ec2.internal  |  172.31.16.12  |  ec2-54-91-10-94.compute-1.amazonaws.com    |  54.91.10.94   |  running     |
|  i-00661d437d277dd62|  d2iq-cp3       |  ip-172-31-24-21.ec2.internal  |  172.31.24.21  |  ec2-54-221-81-108.compute-1.amazonaws.com  |  54.221.81.108 |  running     |
|  i-00ca5701d534a5a04|  d2iq-bootstrap |  ip-172-31-18-41.ec2.internal  |  172.31.18.41  |  ec2-54-221-185-20.compute-1.amazonaws.com  |  54.221.185.20 |  running     |
+---------------------+-----------------+--------------------------------+----------------+---------------------------------------------+----------------+--------------+
```

## Generate environment variable exports

run `scripts/gen-export-statements`. This script will generate an `export` statement for the _private_ IP address of each  VM, and the public DNS name for those VMs that have one. You will use these environment variables going forward:

```
scripts/gen-export-statements
```

## Define environment variables

Paste the output of the above command in the dev environment console. Also save the output in a text editor for use later. Example:
```
export d2iq_bootstrap=172.31.18.41
export d2iq_bootstrap_private_dns_name=ip-172-31-18-41.ec2.internal
export d2iq_bootstrap_public_dns_name=ec2-54-221-185-20.compute-1.amazonaws.com
export d2iq_cp1=172.31.16.12
export d2iq_cp1_private_dns_name=ip-172-31-16-12.ec2.internal
export d2iq_cp1_public_dns_name=ec2-54-91-10-94.compute-1.amazonaws.com
export d2iq_cp2=172.31.16.51
export d2iq_cp2_private_dns_name=ip-172-31-16-51.ec2.internal
export d2iq_cp2_public_dns_name=ec2-54-83-92-172.compute-1.amazonaws.com
export d2iq_cp3=172.31.24.21
export d2iq_cp3_private_dns_name=ip-172-31-24-21.ec2.internal
export d2iq_cp3_public_dns_name=ec2-54-221-81-108.compute-1.amazonaws.com
export d2iq_w1=172.31.23.222
export d2iq_w1_private_dns_name=ip-172-31-23-222.ec2.internal
export d2iq_w1_public_dns_name=ec2-54-91-101-122.compute-1.amazonaws.com
export d2iq_w2=172.31.28.98
export d2iq_w2_private_dns_name=ip-172-31-28-98.ec2.internal
export d2iq_w2_public_dns_name=ec2-54-226-101-241.compute-1.amazonaws.com
export d2iq_w3=172.31.29.80
export d2iq_w3_private_dns_name=ip-172-31-29-80.ec2.internal
export d2iq_w3_public_dns_name=ec2-54-90-155-110.compute-1.amazonaws.com
```

## Provision a load balancer

Provision a load balancer over the worker VMs to support access to the workloads from outside of the cluster:
```
scripts/create-nlb EVO d2iq-w
```