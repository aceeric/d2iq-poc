# Configure the bootstrap VM

**Context: Bootstrap VM**

## Install Docker

On completion, the snippet below will log you out of the bootstrap VM in order that the docker permissions can take effect. So after this step, log back in to the bootstrap VM:
```
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
sudo groupadd docker
sudo usermod -aG docker $USER
exit
```

> **LOG BACK INTO THE BOOTSTRAP VM NOW**

## Confirm Docker
```
docker info
```

## Kubectl
```
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubectl version --client
```

## Helm 3
```
curl -sL https://get.helm.sh/helm-v3.9.2-linux-386.tar.gz -o /tmp/helm-v3.9.2-linux-386.tar.gz
tar -zxvf /tmp/helm-v3.9.2-linux-386.tar.gz -C /tmp
sudo mv /tmp/linux-386/helm /usr/sbin/helm && rm -rf /tmp/helm-v3.9.2-linux-386.tar.gz /tmp/linux-386
helm version
```

## Private Docker Registry

The private registry will be secured by a self-signed cert.

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

Or the `dpk` command on the bootstrap VM fails. Unclear why:
```
sudo cp ca.pem /etc/pki/ca-trust/source/anchors/private-registry.ca
sudo update-ca-trust
sudo grep registryroot /etc/pki/tls/certs/ca-bundle.crt
```

Should produce:
```
# registryroot
```

### Add registry CA to OS truststore on all cluster VMs

Enable all cluster VMs to pull from the private registry hosted on the bootstrap VM:
```
for vmip in $d2iq_cp1 $d2iq_cp2 $d2iq_cp3 $d2iq_w1 $d2iq_w2 $d2iq_w3; do\
  scp -i ~/.ssh/d2iq ca.pem $USER@$vmip:.;\
  ssh -t -i ~/.ssh/d2iq $USER@$vmip 'sudo mv ca.pem /etc/pki/ca-trust/source/anchors/private-registry.ca && sudo update-ca-trust';\
done
```
