#!/usr/bin/python
#
# kvm_syscalls.py
#
# Traces KVM GUEST SYSCALL/SYSRET instructions while SCE bit of the IA32_EFER MSR is unset.
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
import syscall_mapping

ls = 0
correct_cr3_set = 0
db = []
correct_cr3 = 0


def clean_db():
    # for i in db:
    #     print(i)

    # print("\n\n\n")

    counter = 0
    db.append("NIL")

    for i in db:
        if i == "NIL":
            break

        # if int(i[2]) == 12:
        #     correct_cr3 = int(i[1])

    print(correct_cr3)

    for i in range(len(db)):

        if db[counter] == "NIL":
            db.pop(counter)
            break

        # print(str(db[counter][1]) + " : " + str(correct_cr3) + ":" + str(i) + ":" + str(len(db)))
        if int(db[counter][1]) != correct_cr3 and int(db[counter][2]) != 59:
            db.pop(counter)
        else:
            # print(db[i])
            counter = counter + 1

    for i in db:
        print(i)





#func def
def filter_string(index, message):
    match index:
        case 0:
            message[index] = message[index].replace("pid=", "")
        case 1:
            message[index] = message[index].replace("cr3=", "")
        case 2:
            message[index] = message[index].replace("syscall_vector=", "")
        case 3:
            message[index] = message[index].replace("vcpu_number=", "")
        case 4:
            if "NONE" in message[index]:
                message[index] = "NONE"
            else:
                new_index = message[index].index(":")
                message[index] = message[index][new_index + 1:]
                message[index] = message[index].replace(")[UNSAFE-MEMORY]", "")


pid_filter = sys.argv[1:]
pid_filter = list(map(int, pid_filter))

# load BPF program
b = BPF(text="""

TRACEPOINT_PROBE(kvm, kvm_exit) {
    // bpf_trace_printk("PID: %d CR3: %lu", args->pid, args->cr3);
    return 0;
}

""", cflags=["-Wno-macro-redefined"])

# header
print("%-18s %s" % ("TIME", "EVENT"))

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

# print(enabled)

if not enabled:
    enable_kvm_syscall.write("1")
    enable_kvm_syscall.close()


# format output
while 1:
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
    except ValueError:
        continue
    
    if len(pid_filter) == 0:
        # print("%-9s %s" % (strftime("%H:%M:%S"), msg))
        continue
    if pid in pid_filter:
        message = msg.decode(errors='ignore').split()
        for index in range(len(["PID", "CR3","SYSCALL_VECTOR", "VCPU_NUMBER", "PROCESS"])):
            filter_string(index, message)

        if "/usr/bin/ls" in message[4]:
            ls = 1

        if int(message[2]) == 12 and ls == 1 and correct_cr3_set == 0:
            print("CORRECT CR3 FOUND")
            correct_cr3 = int(message[1])
            correct_cr3_set = 1

        if ls == 1:

            # print(message)
            # print("REAL: " + str(message))
            db.append(message)
            if int(message[2]) == 231 and ls == 1 and correct_cr3_set == 1 and int(message[1]) == correct_cr3:
                ls = 0
                correct_cr3_set = 0
                clean_db()
                db.clear()



        # if "=" in msg.decode('utf-8') and "syscall_vector=231" in msg.decode('utf-8'):
        # print("%-9s %s" % (strftime("%H:%M:%S"), msg.decode(errors='ignore')))
        # kvm_syscall_info = msg.decode('utf-8').split(" ")
        # kvm_syscall_info[2] = syscall_mapping.get_syscall_number_x86_64(int(kvm_syscall_info[2][kvm_syscall_info[2].index("=") + 1:]))
        # print(kvm_syscall_info)
        # if kvm_syscall_info[2] == "arch_prctl":
            # print(kvm_syscall_info)