# 2IQ POC

## Intro

This POC assumes you have a Linux development environment with the AWS CLI installed and AWS credentials configured. This environment is referred to throughout these READMEs as your **Dev Env**.

## Steps

Execute the steps in numbered order, beginning with `1-gen-keypair.md`, then `2-provision-vms.md`, and so on.

Throughout this process you will work in various contexts. These READMEs use the convention _Context: X_ to make that clear. Once you see _Context: X_ you will stay in that context until a subsequent _Context: X_.

## Notes

Must places inside code snippets can be copy/pasted directly into the console. However in some cases the code snippet indicates a command **and** its output. In the latter case, the command is prefixed with a dollar sign (`$`) annd the output of the command is not.

Example: this can be pasted directory into the console:
```
ls -l ~
```

In this case, the code snippet is documenting what the expected output of `ls -l ~` would be at a particular point in time:
```
$ ls -l ~
total 43952
-rwxr-xr-x 1 frodo frodo      388 Aug 26 12:22 configure-vm
-rw-rw-r-- 1 frodo frodo 45002752 Aug 26 12:48 kubectl
drwxrwxr-x 3 frodo frodo      153 Aug 26 12:50 pki

```