# Provision infra

## Bootstrap VM

```
./scripts/provision-ec2-instance\
  --dry-run \
  --vol-size 200 \
  --ssh-keys $(pwd)/d2iq \
  project-vpc \
  us-east-subnet-3 \
  devcraft-networking-SecurityGroup-Q6P991Z0L3X6 \
  eVo_AMI_CentOS7 \
  t3.xlarge \
  bootstrap \
  evoforge-user
```

## Control plane

TODO

## Worker

TODO
