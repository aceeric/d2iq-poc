# Configure VMs

**Context Dev VM**

## Copy the VM configuration script into the bootstrap VM:

```
scp -i d2iq scripts/configure-vm ${USER#*\\}@$d2iq_bootstrap:.
```

## SSH in to the bootstrap VM

```
ssh -i d2iq ${USER#*\\}@$d2iq_bootstrap
```

## Configure the cluster VMs

**Context Bootstrap VM**

### Configure login with VM IP addresses

This will set the VM IP address variables on each login:
```
cat <<EOF > ~/.bash_profile
#!/bin/bash
. ${HOME}/.bashrc
EOF
```

Use the values generated earlier:
```
cat <<EOF > ~/.bashrc
export d2iq_bootstrap=10.114.148.19
export d2iq_cp1=10.114.148.29
export d2iq_cp2=10.114.148.55
export d2iq_cp3=10.114.148.17
export d2iq_w1=10.114.148.12
export d2iq_w2=10.114.148.25
export d2iq_w3=10.114.148.22
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

Configure directories for the storage provisioner on the workers. The preflight docs call for 55 GB X 8 drives and mounts. For now, just simulate it with directories.

```
for vmip in $d2iq_w1 $d2iq_w2 $d2iq_w3; do\
  ssh -t -i ~/.ssh/d2iq $USER@$vmip 'for i in 0 1 2 3; do sudo mkdir -p /var/data/volume-$i; done';\
done
```

### Configure the Bootstrap VM

Apply the same configuration that was applied to the cluster VMs to the bootstrap VM. This will restart the bootstrap VM and log you out of the bootstrap VM:
```
source ~/.configure-vm
```
