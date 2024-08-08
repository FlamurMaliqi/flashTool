# Audi Sport | Flash GUI tool
Tool with graphical user interface for simple update process.

## System requirements
- Python 3.12

### Library and dependencies
This tool requires following packages: 
- tkinter 8.6
- paramiko 3.3.1
- scp 0.14.5

## Documentation notes
- The flashing tool stores host address, username and port in to the config file. Syntax of this file is the same as for [ssh config](https://www.ssh.com/academy/ssh/config).
- Paramico SSH-Client follows the [AutoAddPolicy](https://docs.paramiko.org/en/2.4/api/client.html#paramiko.client.AutoAddPolicy) for the host key.
- This setup requires the target system to run a Linux operating system and host an active SSH server. 
- Authentication on the SSH server should involve the use of a username and password.
- Authentication with empty password is not possible. 

