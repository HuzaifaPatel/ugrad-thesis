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
from datetime import datetime
import signal
import sys



pid_filter = list(map(int, sys.argv[1:]))

#key = cr3, value = process_name
cr3_to_process = {}
training_set_local = []

# IN SECONDS
TRAINING_DURATION = 3600



def signal_tstp_handler(sig, frame):
    currently_training = open('currently_training.log', "w")
    for process in training_set_local:
        currently_training.write(process)
    sys.exit(0)




def signal_interrupt_handler(sig, frame):
    currently_training = open('currently_training.log', "w")
    for process in training_set_local:
        currently_training.write(process)
    sys.exit(0)
#SIGNAL TRAP
signal.signal(signal.SIGINT, signal_interrupt_handler)
signal.signal(signal.SIGTSTP, signal_tstp_handler)




def get_time():
    # datetime object containing current date and time
    now = datetime.now()

    return now.strftime("%d/%m/%Y %H:%M:%S")




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




def filter_format(index, kvm_syscall):
    match index:
        case 0:
            kvm_syscall[index] = kvm_syscall[index].replace("pid=", "")
        case 1:
            kvm_syscall[index] = kvm_syscall[index].replace("cr3=", "")
        case 2:
            kvm_syscall[index] = kvm_syscall[index].replace("vector=", "")
        case 3:
            kvm_syscall[index] = kvm_syscall[index].replace("vcpu_number=", "")
        case 4:
            if "NONE" in kvm_syscall[index]:
                kvm_syscall[index] = "NONE"
            else:
                new_index = kvm_syscall[index].index(":")
                kvm_syscall[index] = kvm_syscall[index][new_index + 1:]
                kvm_syscall[index] = kvm_syscall[index].replace(")[UNSAFE-MEMORY]", "")




def populate_currently_trained():
    currently_training = open('currently_training.log', "a+")
    for training_set in currently_training:
        training_set_backup.append(training_set) 

    currently_training.close()  




def add_cr3_to_dict(cr3, process):
    cr3_to_process[cr3] = process




def should_train_process(PROCESS):
    combined_training_set_local = '\n'.join(training_set_local)

    if PROCESS not in combined_training_set_local:
        return True
    return False




def train_process(PROCESS, VECTOR, PID):
    training_set_local.append(PROCESS + ":" + get_time() + "\n")

    process = PROCESS.replace("/", "@")
    if PID == ".":
        process = process[1:]

    process_filename = "training_dataset/" + process
    new_process_file = open(process_filename, 'a+')
    new_process_file.close()



def add_syscall_to_training_set(CR3, VECTOR):
    process = cr3_to_process[CR3].replace("/", "@")

    process_filename = "training_dataset/" + process
    process_file = open(process_filename, "a+")
    process_file.write(VECTOR + "\n")
    process_file.close()




def get_kvm_syscalls():
    enable_tracepoint()
    populate_currently_trained()

    trace = BPF(text="""""", cflags=["-Wno-macro-redefined"])

    while 1:
        try:
            (task, pid, cpu, flags, ts, msg) = trace.trace_fields()
        except ValueError:
            continue

        kvm_syscall = msg.decode(errors='ignore').split()

        for index in range(len(["PID", "CR3","SYSCALL_VECTOR", "VCPU_NUMBER", "PROCESS"])):
            filter_format(index, kvm_syscall)


        PID         = kvm_syscall[0]
        CR3         = kvm_syscall[1]
        VECTOR      = kvm_syscall[2]
        VCPU_NUMBER = kvm_syscall[3]
        PROCESS     = kvm_syscall[4]


        #for all training
            # if training_duration == TRAINING DURATION
                # create sequences
                # move to normal profile


        # if execve
        if "NONE" not in PROCESS:
            add_cr3_to_dict(CR3, PROCESS)
            
            if should_train_process(PROCESS):
                train_process(PROCESS, VECTOR, PID)


        if CR3 in cr3_to_process:
            add_syscall_to_training_set(CR3, VECTOR)

            # if exit_group and cr3 being tracked (to avoid key error)
            if int(VECTOR) == 231 and CR3 in cr3_to_process:
                cr3_to_process.pop(CR3)



get_kvm_syscalls()