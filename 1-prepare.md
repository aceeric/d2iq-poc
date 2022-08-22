# Prepare

All instructions assume you are in the repository root.

## Generate SSH key pair

This key pair will be added to all VMs to support passwordless ssh:

```
ssh-keygen -t ed25519 -N '' -f d2iq <<<y
```
