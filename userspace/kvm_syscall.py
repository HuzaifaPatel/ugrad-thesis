#!/usr/bin/python
#
# kvm_syscalls.py
#
# Traces KVM GUEST system calls while SCE bit of the EFER MSR is unset.
# See kvm_syscall.txt for more information.
# 
#
#
# Copyright (c) 2022 Huzaifa Patel.
#
# Author:
#   Huzaifa Patel <huzaifa.patel@carleton.ca>


from __future__ import print_function
from bcc import BPF
from time import strftime

# load BPF program
b = BPF(text="""

TRACEPOINT_PROBE(kvm, kvm_syscall) {

    bpf_trace_printk("PID: %d System Call: %s\\n", args->pid, args->syscall_name);
    return 0;
}

""")

# header
print("%-18s %s" % ("TIME", "EVENT"))

# format output
while 1:
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
    except ValueError:
        continue
    print("%-9s %s" % (strftime("%H:%M:%S"), msg))
