c # PyCracker
An advanced python SSH cracker and infector. Aimed to be simple to use, simple to develop.

## Dependencies
* paramiko
* python3

Make sure you use paramiko for python3!

## How it works
The tool loads a list of ips and tries to crack the ssh authentication protocol. If the creditentials match, the ip is stored in a txt file along with the username and password.)

 The following parameters are configurable:
 
 * Threads count (threshold for total concurrent connections)
 * Creditentials file (colon separated "login:pass" file)
 * Command (run a custom command on each cracked host)
 
## Command line options
```
./pycracker.py -h
usage: pycracker.py [-h] [-C CREDS] [-t THREADS] [--command COMMAND] ip_file

An advanced python SSH cracker and infector. Aimed to be simple to use, simple to develop.

positional arguments:
  ip_file               list of servers to attack, one entry per line

optional arguments:
  -h, --help            show this help message and exit
  -C CREDS, --creds CREDS
                        colon separated "login:pass" file
  -t THREADS, --threads THREADS
                        run with n threads
  --command COMMAND     execute a command on the host
```
