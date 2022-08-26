# Provision VMs

**Context: Dev Env**

## Provision the VMS
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

## Use this to wait for all the VMs to be ready
```
aws ec2 describe-instances --filters "Name=tag:Name,Values=d2iq*"\
  --query "Reservations[*].Instances[*].{name: Tags[?Key=='Name'] | [0].Value, instance_id: InstanceId, private_ip: PrivateIpAddress, private_dns: PrivateDnsName, public_ip: PublicIpAddress, public_dns: PublicDnsName, state: State.Name}"\
  --output table
```

## Generate environment variable exports
```
while read line; do\
  line=($line);\
  vmname=${line[0]};\
  ip=${line[1]};\
  echo "export ${vmname/-/_}=$ip";\
done < <(aws ec2 describe-instances --filters "Name=tag:Name,Values=d2iq*"\
  --query "Reservations[*].Instances[*].[Tags[?Key=='Name']| [0].Value,PrivateIpAddress]"\
  --output text | sort)
```

## Define env vars and save in a text editor

Paste the output of the above command in the dev environment console. Also save the output in a text editor for use later. Example:
```
export d2iq_bootstrap=10.114.148.19
export d2iq_cp1=10.114.148.29
export d2iq_cp2=10.114.148.55
export d2iq_cp3=10.114.148.17
export d2iq_w1=10.114.148.12
export d2iq_w2=10.114.148.25
export d2iq_w3=10.114.148.22
```

## Configure known hosts TODO CONSIDER JUST STRICT HOST CHECKING NO LS CUZ THIS NOT WORKEE

This will configure your known hosts file to avoid fingerprint collisions and yes/no prompts when ssh'ing into the VMs the first time:
```
for vmip in $d2iq_bootstrap $d2iq_cp1 $d2iq_cp2 $d2iq_cp3 $d2iq_w1 $d2iq_w2 $d2iq_w3; do\
  sed -i "/$vmip/d" ~/.ssh/known-hosts && ssh-keyscan -t ecdsa $vmip >> ~/.ssh/known-hosts;\
done
```
