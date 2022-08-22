# Configure the bootstrap VM

```
ssh -i ./d2iq -o 'StrictHostKeyChecking no' esace@ip-10-114-148-44.ec2.internal
```

## Set SELinux disabled
```
sudo sed -e 's/SELINUX=enforcing/SELINUX=disabled/' -i /etc/selinux/config
sudo shutdown -r now
```

SSH Back in to the instance.

## Docker
```
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
sudo groupadd docker
sudo usermod -aG docker $USER
sudo shutdown now -r
```

## Kubectl
```
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

## Helm 3
```
curl -sL https://get.helm.sh/helm-v3.9.2-linux-386.tar.gz -o /tmp/helm-v3.9.2-linux-386.tar.gz
tar -zxvf /tmp/helm-v3.9.2-linux-386.tar.gz -C /tmp
sudo mv /tmp/linux-386/helm /usr/sbin/helm && rm -rf /tmp/helm-v3.9.2-linux-386.tar.gz /tmp/linux-386
```

## Private Docker Registry

### Set directory context
```
mkdir ~/pki && cd ~/pki
```

### Generate registry CA
```
openssl genrsa -out ca-key.pem 2048
openssl req -x509 -new -nodes -key ca-key.pem -sha256 -subj "/CN=registryroot" -days 10000 -out ca.pem
```

### Generate registry cert/key
```
openssl genrsa -out registry-key.pem 2048

cat <<EOF > csr.conf
[ req ]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn

[ dn ]
CN = $(hostname)

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = $(hostname)
DNS.2 = localhost
IP.1 = $(hostname -i)
IP.2 = 127.0.0.1

[ v3_ext ]
authorityKeyIdentifier=keyid,issuer:always
basicConstraints=CA:FALSE
keyUsage=keyEncipherment,dataEncipherment,digitalSignature,nonRepudiation
extendedKeyUsage=serverAuth,clientAuth
subjectAltName=@alt_names
EOF

openssl req -new -key registry-key.pem -out registry.csr -config csr.conf

openssl x509 -req -in registry.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out registry-cert.pem\
  -days 10000 -extensions v3_ext -extfile csr.conf
```

### Isolate registry cert/key
```
mkdir registry
cp registry-cert.pem registry/registry.crt
cp registry-key.pem registry/registry.key
```

### Configure docker daemon to trust the registry cert
```
sudo mkdir -p /etc/docker/certs.d/$(hostname):5000
sudo cp ca.pem /etc/docker/certs.d/$(hostname):5000/ca.crt
```

### Run the registry
```
docker run -d\
  --restart=always\
  --name registry\
  -v ~/pki/registry:/certs\
  -e REGISTRY_HTTP_ADDR=0.0.0.0:5000\
  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/registry.crt\
  -e REGISTRY_HTTP_TLS_KEY=certs/registry.key\
  -p 5000:5000\
  registry:2.7.1
```

### Verify
```
docker pull gcr.io/google-containers/busybox:latest
docker tag gcr.io/google-containers/busybox:latest $(hostname):5000/busybox:latest
docker push $(hostname):5000/busybox:latest
```

If successful, then the private registry is configured.

### Add registry CA to OS truststore

Or the `dpk` command on the bootstrap VM fails:
```
sudo cp ca.pem /etc/pki/ca-trust/source/anchors/private-registry.ca
sudo update-ca-trust
sudo grep registryroot /etc/pki/tls/certs/ca-bundle.crt
```

Should produce:
```
# registryroot
```

## Get D2IQ tarball and inflate it

```
cd ~

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
