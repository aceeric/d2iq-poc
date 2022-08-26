# 2IQ POC

Stands up a D2IQ Kubernetes cluster in AWS with 3 control plane servers and 3 worker nodes. Uses the air-gapped tarball from D2IQ.

## Pre-requisites

This POC assumes you have a Linux development environment with the AWS CLI installed and AWS credentials configured. This dev environment is referred to throughout these READMEs as your **Dev Env**. The POC also assumes you have privileges in AWS to manage EC2 instances.

Your AWS environment may differ, or have security constraints, etc. You'll have to adapt the instructions if so. The only imact should be the VM provisioning step. It is expected and required that each VM be able to reach the other via an internal IP, and that the bootstrap vm and one control plane VM are reachable via Public IPs.

This POC does not use a load balancer. The only reason that three control plane VMs are created is because D2IQ does not have documentation on how to stand up a single control-plane VM cluster.

## Steps

Execute the steps in numbered order, beginning with `01-gen-keypair.md`, then `02-provision-vms.md`, and so on.

Throughout this process you will work in various contexts. These READMEs use the convention _Context: X_ to make that clear. Once you see _Context: X_ you will stay in that context until a subsequent _Context: X_.

## Notes

Most code snippets are intended to be copy/pasted directly into the console. However in some cases the code snippet indicates a command **and** its output. In the latter case, the command is prefixed with a dollar sign (`$`) and the output of the command is not. Examples:

This snippet can be pasted directly into the console:
```
ls -l ~
```

In contrast, this snippet is documenting what the expected output of `ls -l ~` should be at a particular point in time:
```
$ ls -l ~
total 43952
-rwxr-xr-x 1 frodo frodo      388 Aug 26 12:22 configure-vm
-rw-rw-r-- 1 frodo frodo 45002752 Aug 26 12:48 kubectl
drwxrwxr-x 3 frodo frodo      153 Aug 26 12:50 pki
```