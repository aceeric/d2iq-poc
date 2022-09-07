# AWS Load Balancer POC (eVo)

A POC to validate programmatically creating an AWS network load balancer and connecting it to a pool of EC2 instances. This POC performed from an AWS Workspaces virtual desktop.

## Create three disposable VMs

```
for vmname in esacelb-1 esacelb-2 esacelb-3; do
  ./scripts/provision-ec2-instance\
    --ssh-keys $(pwd)/d2iq \
    --nowait \
    project-vpc \
    us-east-subnet-3 \
    devcraft-networking-SecurityGroup-Q6P991Z0L3X6 \
    eVo_AMI_CentOS7 \
    t2.small \
    $vmname \
    evoforge-user || break
done
```

## Wait for VMs to start
```
aws ec2 describe-instances --filters "Name=tag:Name,Values=esacelb-*"\
  --query "Reservations[*].Instances[*].{name: Tags[?Key=='Name'] | [0].Value, instance_id: InstanceId, private_ip: PrivateIpAddress, private_dns: PrivateDnsName, public_ip: PublicIpAddress, public_dns: PublicDnsName, state: State.Name}"\
  --output table
```

### Example
```
------------------------------------------------------------------------------------------------------------------------------
|                                                      DescribeInstances                                                     |
+---------------------+------------+---------------------------------+----------------+-------------+------------+-----------+
|     instance_id     |   name     |           private_dns           |  private_ip    | public_dns  | public_ip  |   state   |
+---------------------+------------+---------------------------------+----------------+-------------+------------+-----------+
|  i-0bb492dd770083203|  esacelb-1 |  ip-10-114-148-54.ec2.internal  |  10.114.148.54 |             |  None      |  running  |
|  i-0ead9d24c3a589e8d|  esacelb-3 |  ip-10-114-148-42.ec2.internal  |  10.114.148.42 |             |  None      |  running  |
|  i-0f16f070cbae047c5|  esacelb-2 |  ip-10-114-148-25.ec2.internal  |  10.114.148.25 |             |  None      |  running  |
+---------------------+------------+---------------------------------+----------------+-------------+------------+-----------+
```

## Start a simple HTTPS service on each VM
```
for vmip in 10.114.148.54 10.114.148.42 10.114.148.25; do\
  scp -o 'StrictHostKeyChecking no' -i d2iq scripts/simple-https.py ${USER#*\\}@$vmip:/tmp;\
  scp -i d2iq files/simple-https.service ${USER#*\\}@$vmip:/tmp;\
  ssh -t -i d2iq ${USER#*\\}@$vmip "sudo mv /tmp/simple-https.service /etc/systemd/system";\
  ssh -t -i d2iq ${USER#*\\}@$vmip "sudo systemctl enable --now simple-https";\
done
```

## Verify

Curl the simple HTTP server through the private IP addresses of the VMs. This will emanate a timestamp and hostname from each VM:
```
for vmip in 10.114.148.54 10.114.148.42 10.114.148.25; do\
  curl -k https://$vmip;\
done
```

### Example output
```
2022-09-07 16:12:49.606196 -- ip-10-114-148-54.evoforge.org
2022-09-07 16:12:49.644074 -- ip-10-114-148-42.evoforge.org
2022-09-07 16:12:49.684772 -- ip-10-114-148-25.evoforge.org
```

## Create a load balancer for the VMs
```
scripts/create-nlb EVO esacelb-
```

## Get the load balancer DNS name
```
export LB_DNSNAME=$(aws elbv2 describe-load-balancers --names d2iq-poc --query 'LoadBalancers[0].DNSName' | tr -d '"')
```

### Example
```
d2iq-poc-5420a09d383241d7.elb.us-east-1.amazonaws.com
```

## Access the service using the load balancer IP address
```
while true; do curl -k https://$LB_DNSNAME; done
```

### Observe that the responses are (generally) round-robin
```
2022-09-07 16:11:24.812113 -- ip-10-114-148-42.evoforge.org
2022-09-07 16:11:24.849456 -- ip-10-114-148-25.evoforge.org
2022-09-07 16:11:24.883846 -- ip-10-114-148-42.evoforge.org
2022-09-07 16:11:26.939643 -- ip-10-114-148-42.evoforge.org
2022-09-07 16:11:26.976940 -- ip-10-114-148-54.evoforge.org
2022-09-07 16:11:27.009317 -- ip-10-114-148-25.evoforge.org
2022-09-07 16:11:27.040387 -- ip-10-114-148-25.evoforge.org
2022-09-07 16:11:27.079936 -- ip-10-114-148-42.evoforge.org
2022-09-07 16:11:27.111958 -- ip-10-114-148-42.evoforge.org
2022-09-07 16:11:27.141958 -- ip-10-114-148-25.evoforge.org
2022-09-07 16:11:27.186009 -- ip-10-114-148-54.evoforge.org
2022-09-07 16:11:27.238969 -- ip-10-114-148-42.evoforge.org
2022-09-07 16:11:27.292951 -- ip-10-114-148-25.evoforge.org
2022-09-07 16:11:27.333434 -- ip-10-114-148-42.evoforge.org
2022-09-07 16:11:27.365110 -- ip-10-114-148-42.evoforge.org
2022-09-07 16:11:27.400079 -- ip-10-114-148-54.evoforge.org
2022-09-07 16:11:27.438416 -- ip-10-114-148-25.evoforge.org
2022-09-07 16:11:27.471689 -- ip-10-114-148-25.evoforge.org
2022-09-07 16:11:27.509697 -- ip-10-114-148-25.evoforge.org
2022-09-07 16:11:27.539073 -- ip-10-114-148-42.evoforge.org
2022-09-07 16:11:27.586974 -- ip-10-114-148-54.evoforge.org
2022-09-07 16:11:27.622343 -- ip-10-114-148-54.evoforge.org
2022-09-07 16:11:27.653970 -- ip-10-114-148-54.evoforge.org
2022-09-07 16:11:29.699027 -- ip-10-114-148-54.evoforge.org
2022-09-07 16:11:31.739850 -- ip-10-114-148-54.evoforge.org
2022-09-07 16:11:31.770184 -- ip-10-114-148-25.evoforge.org
2022-09-07 16:11:31.831310 -- ip-10-114-148-25.evoforge.org
```

etc...

## Cleanup

### Remove the LB

scripts/create-nlb EVO ignored CLEANUP

### Remove the VMs
```
aws ec2 describe-instances --filters "Name=tag:Name,Values=esacelb*" --query 'Reservations[*].Instances[?!contains(State.Name, '"'terminated'"')].InstanceId' --output text | while read instanceid; do aws ec2 terminate-instances --instance-ids $instanceid; done
```