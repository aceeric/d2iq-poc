# Configure VMs

**Context Dev VM**

## Copy the VM configuration script into the bootstrap VM:

Public AWS:
```
scp -o 'StrictHostKeyChecking no' -i d2iq scripts/configure-vm ${USER#*\\}@$d2iq_bootstrap_public_dns_name:.
```

eVo:
```
scp -i d2iq scripts/configure-vm ${USER#*\\}@$d2iq_bootstrap:.
```

## SSH in to the bootstrap VM


Public AWS:
```
ssh -i d2iq ${USER#*\\}@$d2iq_bootstrap_public_dns_name
```

eVo:
```
ssh -i d2iq ${USER#*\\}@$d2iq_bootstrap
```

## Configure the cluster VMs

**Context: Bootstrap VM**

### Configure user login with VM IP addresses

This will set the VM IP address variables on each login to the bootstrap VM:
```
cat <<EOF > ~/.bash_profile
#!/bin/bash
. ${HOME}/.bashrc
EOF
```

> Use the values generated earlier:
```
cat <<EOF > ~/.bashrc
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
EOF

source ~/.bashrc
```

### Configure the cluster VMs
This will restart each cluster VM:

```
for vmip in $d2iq_cp1 $d2iq_cp2 $d2iq_cp3 $d2iq_w1 $d2iq_w2 $d2iq_w3; do\
  scp -o 'StrictHostKeyChecking no' -i ~/.ssh/d2iq ~/configure-vm $USER@$vmip:.;\
  ssh -t -i ~/.ssh/d2iq $USER@$vmip 'source ~/configure-vm';\
done
```
### Configure worker storage

Wait a moment for the VMs to come back up after the prior step:

```
$ for w in $d2iq_w1 $d2iq_w2 $d2iq_w3; do ssh -i ~/.ssh/d2iq $USER@$w ls -l; done
total 4
-rwxr-xr-x. 1 eace eace 630 Aug 28 14:15 configure-vm
total 4
-rwxr-xr-x. 1 eace eace 630 Aug 28 14:15 configure-vm
total 4
-rwxr-xr-x. 1 eace eace 630 Aug 28 14:15 configure-vm
-bash-4.2$ 
```

Configure directories for the storage provisioner on the workers. The preflight docs call for 55 GB X 8 drives and mounts. For now, just simulate that with directories.

```
for vmip in $d2iq_w1 $d2iq_w2 $d2iq_w3; do\
  ssh -t -i ~/.ssh/d2iq $USER@$vmip 'for i in 0 1 2 3; do sudo mkdir -p /var/data/volume-$i; done';\
done
```

### Configure the Bootstrap VM

Apply the same configuration that was applied to the cluster VMs to the bootstrap VM. This will restart the bootstrap VM and log you out of the bootstrap VM, so SSH back in to the bootstrap VM when this completes:
```
source ~/configure-vm
```

> **LOG BACK INTO THE BOOTSTRAP VM NOW**
