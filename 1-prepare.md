# Prepare

All instructions assume you are in the repository root.

## Generate SSH key pair

This key pair will be added to all VMs to support passwordless ssh. The private key permissions are set as required by ssh.

```
ssh-keygen -t ed25519 -N '' -f d2iq <<<y && chmod 600 ./d2iq
```
