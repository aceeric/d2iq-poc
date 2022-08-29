# Get D2IQ tarball and copy files to cluster VMs

**Context: Bootstrap VM**

## Get D2IQ tarball and inflate it
```
sudo mkdir /var/d2iq && sudo chown $USER /var/d2iq && cd /var/d2iq

curl -fL\
  https://s3.amazonaws.com/se.downloads.d2iq/dkp/v2.2.2/dkp_airgapped_bundle_v2.2.2_linux_amd64.tar.gz\
  -o dkp_airgapped_bundle_v2.2.2_linux_amd64.tar.gz

tar -zxvf dkp_airgapped_bundle_v2.2.2_linux_amd64.tar.gz &&\
  rm -f dkp_airgapped_bundle_v2.2.2_linux_amd64.tar.gz
```

## ADDED MONDAY 29-AUG

An additional gz is needed per D2IQ in the `kib` directory. (Location is important here.)
```
curl -fL\
  https://packages.d2iq.com/dkp/containerd/containerd-1.4.13-d2iq.1-centos-7.9-x86_64.tar.gz\
  -o /var/d2iq/dkp-v2.2.2/kib/containerd-1.4.13-d2iq.1-centos-7.9-x86_64.tar.gz
```

## Load the Konvoy bootstrap image

```
docker load -i dkp-v2.2.2/konvoy-bootstrap_v2.2.2.tar
```

## Seed the docker bootstrap registry
```
dkp-v2.2.2/dkp push image-bundle\
  --image-bundle dkp-v2.2.2/konvoy_image_bundle_v2.2.2_linux_amd64.tar.gz\
  --to-registry $(hostname):5000
```

## Verify
```
curl -s https://$(hostname):5000/v2/_catalog\
  | python -c 'import json, sys; print(json.dumps(json.loads(sys.stdin.read()), indent=4, sort_keys=True))'
```

## Copy artifacts to hosts

This uses the `d2iq-konvoy` utility to copy artifacts to all the cluster VMs.

### Set env vars
```
export VERSION=1.22.8
export BUNDLE_OS=centos_7_x86_64
export CONTROL_PLANE_1_ADDRESS=$d2iq_cp1
export CONTROL_PLANE_2_ADDRESS=$d2iq_cp2
export CONTROL_PLANE_3_ADDRESS=$d2iq_cp3
export WORKER_1_ADDRESS=$d2iq_w1
export WORKER_2_ADDRESS=$d2iq_w2
export WORKER_3_ADDRESS=$d2iq_w3
export SSH_USER=$USER
export SSH_PRIVATE_KEY_FILE=~/.ssh/d2iq
```

### Directory context:
```
cd /var/d2iq/dkp-v2.2.2/kib
```

### Generate inventory.yaml

This yaml includes a timeout specifier to overcome `konvoy-image upload` timeouts experienced in AWS.
```
mv inventory.yaml inventory.yaml.original
cat <<EOF > inventory.yaml
all:
  vars:
    ansible_user: $SSH_USER
    ansible_port: 22
    ansible_ssh_private_key_file: $SSH_PRIVATE_KEY_FILE
    ansible_timeout: 2000
  hosts:
    $CONTROL_PLANE_1_ADDRESS:
      ansible_host: $CONTROL_PLANE_1_ADDRESS
    $CONTROL_PLANE_2_ADDRESS:
      ansible_host: $CONTROL_PLANE_2_ADDRESS
    $CONTROL_PLANE_3_ADDRESS:
      ansible_host: $CONTROL_PLANE_3_ADDRESS
    $WORKER_1_ADDRESS:
      ansible_host: $WORKER_1_ADDRESS
    $WORKER_2_ADDRESS:
      ansible_host: $WORKER_2_ADDRESS
    $WORKER_3_ADDRESS:
      ansible_host: $WORKER_3_ADDRESS
EOF
```

### Move artifacts under `kib/artifacts` directory per D2IQ
```
mkdir -p ./artifacts/images
cp -r ../artifacts/images ./artifacts
cp ../artifacts/"$VERSION"_"$BUNDLE_OS".tar.gz ./artifacts
cp ../artifacts/pip-packages.tar.gz ./artifacts
```

### Verify
```
$ find containerd* artifacts -type f | sort
artifacts/1.22.8_centos_7_x86_64.tar.gz
artifacts/images/1.22.8_images_fips.tar.gz
artifacts/images/1.22.8_images.tar.gz
artifacts/pip-packages.tar.gz
containerd-1.4.13-d2iq.1-centos-7.9-x86_64.tar.gz
```

### Upload
```
./konvoy-image -v6 upload artifacts\
  --container-images-dir=./artifacts/images/\
  --os-packages-bundle=./artifacts/"$VERSION"_"$BUNDLE_OS".tar.gz\
  --pip-packages-bundle=./artifacts/pip-packages.tar.gz\
  --containerd-bundle=./containerd-1.4.13-d2iq.1-centos-7.9-x86_64.tar.gz
```

> **NOTE**: If the `konvoy-image` upload times out, you may need modify `/var/d2iq/dkp-v2.2.2/kib/ansible/roles/offline/tasks/upload.yaml` and add a `timeout` statement to the `upload containerd bundle to remote` task. E.g.:
```
...
    - name: upload containerd bundle to remote
      timeout: 10000 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< ADDED
      copy:
        src: "{{ containerd_local_bundle_file }}"
        dest: "{{ containerd_remote_bundle_path }}/{{ containerd_tar_file }}"
  when: containerd_local_bundle_file != ""
```

Success looks like:
```
PLAY RECAP *********************************************************************
172.31.22.222 : ok=24 changed=14 unreachable=0 failed=0 skipped=1 rescued=0 ignored=0   
172.31.22.74  : ok=24 changed=14 unreachable=0 failed=0 skipped=1 rescued=0 ignored=0   
172.31.26.96  : ok=24 changed=14 unreachable=0 failed=0 skipped=1 rescued=0 ignored=0   
172.31.28.104 : ok=24 changed=14 unreachable=0 failed=0 skipped=1 rescued=0 ignored=0   
172.31.30.206 : ok=24 changed=14 unreachable=0 failed=0 skipped=1 rescued=0 ignored=0   
172.31.31.56  : ok=24 changed=14 unreachable=0 failed=0 skipped=1 rescued=0 ignored=0   
```
