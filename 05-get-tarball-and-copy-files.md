# Get D2IQ tarball and copy files to cluster VMS

**Context Bootstrap VM**

## Get D2IQ tarball and inflate it
```
sudo mkdir /var/d2iq && sudo chown $USER /var/d2iq && cd /var/d2iq

curl -fL\
  https://s3.amazonaws.com/se.downloads.d2iq/dkp/v2.2.2/dkp_airgapped_bundle_v2.2.2_linux_amd64.tar.gz\
  -o dkp_airgapped_bundle_v2.2.2_linux_amd64.tar.gz

tar -zxvf dkp_airgapped_bundle_v2.2.2_linux_amd64.tar.gz
rm -f dkp_airgapped_bundle_v2.2.2_linux_amd64.tar.gz
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

## Copy artifacts to hosts

This uses the `d2iq-konvoy` utility

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

This yaml includes a timeout specifier to overcome `konvoy-image upload` timeouts.
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

### Move artifacts under `kib` directory per D2IQ
```
mkdir -p ./artifacts/images
cp -r ../artifacts/images ./artifacts
cp ../artifacts/"$VERSION"_"$BUNDLE_OS".tar.gz ./artifacts
cp ../artifacts/pip-packages.tar.gz ./artifacts
```

### Verify
```
$ find artifacts -type f | sort
artifacts/1.22.8_centos_7_x86_64.tar.gz
artifacts/images/1.22.8_images_fips.tar.gz
artifacts/images/1.22.8_images.tar.gz
artifacts/pip-packages.tar.gz
```

### Upload
```
./konvoy-image -v6 upload artifacts\
  --container-images-dir=./artifacts/images/\
  --os-packages-bundle=./artifacts/"$VERSION"_"$BUNDLE_OS".tar.gz\
  --pip-packages-bundle=./artifacts/pip-packages.tar.gz
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
10.114.148.12 : ok=20  changed=1  unreachable=0  failed=0  skipped=5  rescued=0  ignored=0   
10.114.148.17 : ok=20  changed=1  unreachable=0  failed=0  skipped=5  rescued=0  ignored=0   
10.114.148.22 : ok=20  changed=1  unreachable=0  failed=0  skipped=5  rescued=0  ignored=0   
10.114.148.25 : ok=20  changed=1  unreachable=0  failed=0  skipped=5  rescued=0  ignored=0   
10.114.148.29 : ok=20  changed=1  unreachable=0  failed=0  skipped=5  rescued=0  ignored=0   
10.114.148.55 : ok=20  changed=1  unreachable=0  failed=0  skipped=5  rescued=0  ignored=0   
```
