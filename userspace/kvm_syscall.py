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

pid_filter = sys.argv[1:]
pid_filter = list(map(int, pid_filter))

# load BPF program
b = BPF(text="""

TRACEPOINT_PROBE(kvm, kvm_syscall) {
    // bpf_trace_printk("PID: %d CR3: %lu", args->pid, args->cr3);
    return 0;
}

""", cflags=["-Wno-macro-redefined"])

# header
print("%-18s %s" % ("TIME", "EVENT"))


# this assumes the owner is root
os.chmod("/sys/kernel", 0o777)
os.chmod("/sys/kernel/tracing", 0o777)
os.chmod("/sys/kernel/tracing/events", 0o777)
os.chmod("/sys/kernel/tracing/events/kvm", 0o777)
os.chmod("/sys/kernel/tracing/events/kvm/kvm_syscall", 0o777)
os.chmod("/sys/kernel/tracing/events/kvm/kvm_syscall/enable", 0o777)

# open and write '1' to file to enable tracepoint
enable_kvm_syscall = open("/sys/kernel/tracing/events/kvm/kvm_syscall/enable", "w+")

enabled = int(enable_kvm_syscall.read(1))

print(enabled)

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
        # if "=" in msg.decode('utf-8') and "syscall_vector=231" in msg.decode('utf-8'):
        # print("%-9s %s" % (strftime("%H:%M:%S"), msg.decode(errors='ignore')))
        # kvm_syscall_info = msg.decode('utf-8').split(" ")
        # kvm_syscall_info[2] = syscall_mapping.get_syscall_number_x86_64(int(kvm_syscall_info[2][kvm_syscall_info[2].index("=") + 1:]))
        # print(kvm_syscall_info)
        # if kvm_syscall_info[2] == "arch_prctl":
            # print(kvm_syscall_info)


        