# Prepare

All instructions assume you have git cloned this repo and you are in the repository root directory.

## Generate SSH key pair

**Context: Dev Env**

This key pair will be added to all VMs by the provisioning step to support passwordless ssh. The private key permissions are set as required by ssh.

```
ssh-keygen -t ed25519 -N '' -f d2iq <<<y && chmod 600 ./d2iq
```
