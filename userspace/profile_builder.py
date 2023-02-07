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

    return now.strftime("%Y:%m:%d:%H:%M:%S")




def sanitize_time(time):
    time.pop(0)
    time[5] = time[5].replace("\n","")
    return time




def is_trained(compared_time):
    current_time = get_time().split(":")

    # datetime(year, month, day, hour, minute, second)
    new_time = datetime(
                            int(current_time[0]), 
                            int(current_time[1]), 
                            int(current_time[2]), 
                            int(current_time[3]), 
                            int(current_time[4]), 
                            int(current_time[5]))

    old_time = datetime(
                            int(compared_time[0]), 
                            int(compared_time[1]), 
                            int(compared_time[2]), 
                            int(compared_time[3]), 
                            int(compared_time[4]), 
                            int(compared_time[5]))

    difference = new_time - old_time




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
    currently_training = open('currently_training.log', "r")
    for training_set in currently_training:
        training_set_local.append(training_set) 

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

    process_filename = "training_profile/" + process
    new_process_file = open(process_filename, 'a+')
    new_process_file.close()



def add_syscall_to_training_set(CR3, VECTOR):
    process = cr3_to_process[CR3].replace("/", "@")

    process_filename = "training_profile/" + process
    process_file = open(process_filename, "a+")
    process_file.write(VECTOR + "\n")
    process_file.close()


def add_sequence(CR3, PROCESS, PID):
    

    #_________________________________________________
    #CREATE SEQUENCES FILE START
    process = PROCESS.replace("/", "@")

    if PID == ".":
        process = process[1:]

    process_filename = "training_profile/" + process
    system_calls = open(process_filename, "r")

    #CREATE SEQUENCES FILE END
    #_________________________________________________



    #_________________________________________________
    #COPY SYSTEM CALLS LOCALLY START

    syscalls = []

    for system_call in system_calls:
        syscalls.append(system_call[:-1])
    
    system_calls.close()
    #_________________________________________________
    #COPY SYSTEM CALLS LOCALLY STOP




    #_________________________________________________
    # GET OLD SEQUENCES START

    size = 0
    process_sequence = open("sequences/" + process, "a+")
    old_sequences = []

    for old_sequence in process_sequence:
        old_sequences.append(old_sequence[:-1])
        size = size + 1

    process_sequence.close()
    #_________________________________________________
    # GET OLD SEQUENCES END



    #_________________________________________________
    # CREATE SEQUENCES FOR CURRENT SET OF SYSTEM CALLS START
    k = 3
    sequences = []

    for i in range(len(syscalls)):
        if (len(syscalls) - i) >= k:
            potential_sequence = []
            for j in range(k):
                potential_sequence.append(syscalls[i+j])
                if potential_sequence not in sequences and len(potential_sequence) == k:
                    sequences.append(potential_sequence)
    #_________________________________________________
    # CREATE SEQUENCES FOR CURRENT SET OF SYSTEM CALLS END




    #_________________________________________________
    # COMBINE NEW AND OLD SEQUENCES. DON'T COUNT DUPLICATES START    
    for sequence in sequences:
        if sequence not in old_sequences:
            old_sequences.append(sequence)
    #_________________________________________________
    # COMBINE NEW AND OLD SEQUENCES. DON'T COUNT DUPLICATES END




    #_________________________________________________
    # INSERT ALL SEQUENCES INTO FILE IF NEW ONES EXIST START 
    if sequences != old_sequences or size == 0:
        process_sequence = open("sequences/" + process, "w+")

        for i in old_sequences:
            process_sequence.write(str(i) + "\n")

        process_sequence.close()
    #_________________________________________________
    # INSERT ALL SEQUENCES INTO FILE IF NEW ONES EXIST END


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

        for currently_training in training_set_local:
            is_trained(sanitize_time(currently_training.split(":")))

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
            add_sequence(CR3, cr3_to_process[CR3], PID)

            # if exit_group and cr3 being tracked (to avoid key error)
            if int(VECTOR) == 231 and CR3 in cr3_to_process:
                cr3_to_process.pop(CR3)



get_kvm_syscalls()



# process X made 
# insert time of creation of process X
# for i in all_processes
#      