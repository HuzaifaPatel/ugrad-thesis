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

PID = 0
CR3 = 1
VECTOR = 2
VCPU_NUMBER = 3
PROCESS = 4

process_to_cr3 = {}
training_profile = {}
pid_filter = sys.argv[1:]
pid_filter = list(map(int, pid_filter))

def get_time():
    # datetime object containing current date and time
    now = datetime.now()

    return now.strftime("%d/%m/%Y %H:%M:%S")





def filter_format(index, kvm_syscall):
    match index:
        case 0:
            kvm_syscall[index] = kvm_syscall[index].replace("pid=", "")
        case 1:
            kvm_syscall[index] = kvm_syscall[index].replace("cr3=", "")
        case 2:
            kvm_syscall[index] = kvm_syscall[index].replace("syscall_vector=", "")
        case 3:
            kvm_syscall[index] = kvm_syscall[index].replace("vcpu_number=", "")
        case 4:
            if "NONE" in kvm_syscall[index]:
                kvm_syscall[index] = "NONE"
            else:
                new_index = kvm_syscall[index].index(":")
                kvm_syscall[index] = kvm_syscall[index][new_index + 1:]
                kvm_syscall[index] = kvm_syscall[index].replace(")[UNSAFE-MEMORY]", "")




def get_kvm_syscalls():
    global correct_cr3
    global correct_cr3_set
    global ls
    global kvm_syscall


    with open('trace.log') as log:
        for kvm_syscall in log:
            kvm_syscall = kvm_syscall[:-1]
            kvm_syscall = kvm_syscall.replace("['", "").replace("'","")[:-1].split(",")

            for index in range(len(["PID", "CR3","SYSCALL_VECTOR", "VCPU_NUMBER", "PROCESS"])):
                filter_format(index, kvm_syscall)

            # if execve
            if "NONE" not in kvm_syscall[4]:
                # print(kvm_syscall)
                process_to_cr3[str(kvm_syscall[4])] = str(kvm_syscall[1]).replace(" ","")

                currently_training = open('currently_training.log', "a+")
                for training_set in currently_training:
                    print(training_set)
                    # if str(kvm_syscall[4]) not in currently_training:
                    #     currently_training.write(kvm_syscall[4] + ":" + get_time())

                    #     process = kvm_syscall[4].replace("/", "@")
                    #     process_filename = "training_dataset/" + process
                    #     file = open(process_filename, 'a+')
                    #     file.write(kvm_syscall[2] + "\n")
                    #     continue

get_kvm_syscalls()