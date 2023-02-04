#!/usr/bin/python
#
# kvm_syscalls.py
#
# Traces KVM GUEST SYSCALL instruction while SCE bit of the IA32_EFER MSR is unset.
# See kvm_syscall.txt for more information.
# 
#
# Author:
#   Huzaifa Patel <huzaifa.patel@carleton.ca>

from __future__ import print_function
from bcc import BPF
from time import strftime
import time
import sys
import os
from os import listdir
from os.path import isfile, join
import syscall_mapping

PID = 0
CR3 = 1
VECTOR = 2
VCPU_NUMBER = 3
PROCESS = 4

cr3_to_process = {}
training_profile = {}
pid_filter = sys.argv[1:]
pid_filter = list(map(int, pid_filter))

def enable_tracepoint():
    dir_to_tracepoint = [
                        "/sys/kernel", 
                        "/sys/kernel/tracing", 
                        "/sys/kernel/tracing/events", 
                        "/sys/kernel/tracing/events/kvm", 
                        "/sys/kernel/tracing/events/kvm/kvm_syscall", 
                        "/sys/kernel/tracing/events/kvm/kvm_syscall/enable"
                    ]

    # this assumes the uid is root/0
    for path in dir_to_tracepoint:
        os.chmod(path, 0o777)

    # open and write '1' to file to enable tracepoint
    enable_kvm_syscall = open("/sys/kernel/tracing/events/kvm/kvm_syscall/enable", "w+")
    enabled = int(enable_kvm_syscall.read(1))

    if not enabled:
        enable_kvm_syscall.write("1")
        enable_kvm_syscall.close()



def get_kvm_syscalls():
    global correct_cr3
    global correct_cr3_set
    global ls
    global kvm_syscall
    # load BPF program
    enable_tracepoint()
    log = open("trace.log", "a+")
    trace = BPF(text="""

    """, cflags=["-Wno-macro-redefined"])

    # header
    #print("%-18s %s" % ("TIME", "EVENT"))

    # format output
    while 1:
        try:
            (task, pid, cpu, flags, ts, msg) = trace.trace_fields()
        except ValueError:
            continue
        


        if pid in pid_filter:
            kvm_syscall = msg.decode(errors='ignore').split()


            # training_processes = [f for f in listdir("training_dataset") if isfile(join("training_dataset", f))]

            # if "NONE" not in kvm_syscall[4]:
            #print(kvm_syscall)
            log.write(str(kvm_syscall) + "\n")
            log.flush()

            # if str(kvm_syscall[PROCESS]) != "NONE":
            # if "NONE" not in kvm_syscall[PROCESS]:
                # print(kvm_syscall)
            # if str(kvm_syscall[PROCESS]) == "/usr/bin/ls":
            #     if str(kvm_syscall[PROCESS]) not in training_processes:
            #         training_profile[PROCESS] = kvm_syscall[CR3]
            #         process = kvm_syscall[PROCESS].replace("/", "@")
            #         filename = "training_dataset/" + process

            #         file = open(filename, 'a+')
            #         file.write(kvm_syscall[VECTOR])
            #         continue




get_kvm_syscalls()