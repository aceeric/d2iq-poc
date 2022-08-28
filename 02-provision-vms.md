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
    us-east-subnet-3 \
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
i-000b728b18fd217d5  ok
i-0152884dca2c855af  ok
i-0175e14ceb39597bf  ok
i-01f54dac9473609fb  ok
i-03d494c4a9190f704  ok
i-091ae22c8e14e79e0  ok
i-0fd235c61a5117903  ok
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
|  i-000b728b18fd217d5|  d2iq-cp3       |  ip-172-31-28-104.ec2.internal |  172.31.28.104 |  ec2-34-228-255-38.compute-1.amazonaws.com  |  34.228.255.38 |  running     |
|  i-091ae22c8e14e79e0|  d2iq-bootstrap |  ip-172-31-16-26.ec2.internal  |  172.31.16.26  |  ec2-54-88-252-180.compute-1.amazonaws.com  |  54.88.252.180 |  running     |
|  i-0fd235c61a5117903|  d2iq-cp1       |  ip-172-31-26-96.ec2.internal  |  172.31.26.96  |  ec2-54-157-10-215.compute-1.amazonaws.com  |  54.157.10.215 |  running     |
|  i-03d494c4a9190f704|  d2iq-w3        |  ip-172-31-31-56.ec2.internal  |  172.31.31.56  |  ec2-52-205-249-6.compute-1.amazonaws.com   |  52.205.249.6  |  running     |
|  i-0152884dca2c855af|  d2iq-w1        |  ip-172-31-22-74.ec2.internal  |  172.31.22.74  |  ec2-54-226-73-176.compute-1.amazonaws.com  |  54.226.73.176 |  running     |
|  i-0175e14ceb39597bf|  d2iq-cp2       |  ip-172-31-30-206.ec2.internal |  172.31.30.206 |  ec2-54-89-227-109.compute-1.amazonaws.com  |  54.89.227.109 |  running     |
|  i-01f54dac9473609fb|  d2iq-w2        |  ip-172-31-22-222.ec2.internal |  172.31.22.222 |  ec2-54-87-102-18.compute-1.amazonaws.com   |  54.87.102.18  |  running     |
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
export d2iq_bootstrap=172.31.16.26
export d2iq_bootstrap_dns_name=ec2-54-88-252-180.compute-1.amazonaws.com
export d2iq_cp1=172.31.26.96
export d2iq_cp1_dns_name=ec2-54-157-10-215.compute-1.amazonaws.com
export d2iq_cp2=172.31.30.206
export d2iq_cp2_dns_name=ec2-54-89-227-109.compute-1.amazonaws.com
export d2iq_cp3=172.31.28.104
export d2iq_cp3_dns_name=ec2-34-228-255-38.compute-1.amazonaws.com
export d2iq_w1=172.31.22.74
export d2iq_w1_dns_name=ec2-54-226-73-176.compute-1.amazonaws.com
export d2iq_w2=172.31.22.222
export d2iq_w2_dns_name=ec2-54-87-102-18.compute-1.amazonaws.com
export d2iq_w3=172.31.31.56
export d2iq_w3_dns_name=ec2-52-205-249-6.compute-1.amazonaws.com
```
