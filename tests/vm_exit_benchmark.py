import os
from bcc import BPF
from time import time

end = time() + 3600
vm_exit_zero_counter = 0
vm_exit_thirty_two_counter = 0

def enable_tracepoint():
    dir_to_tracepoint = [
                        "/sys/kernel", 
                        "/sys/kernel/tracing", 
                        "/sys/kernel/tracing/events", 
                        "/sys/kernel/tracing/events/kvm", 
                        "/sys/kernel/tracing/events/kvm/kvm_exit", 
                        "/sys/kernel/tracing/events/kvm/kvm_exit/enable"
                    ]

    # this assumes the uid is root/0
    for path in dir_to_tracepoint:
        os.chmod(path, 0o777)

    # open and write '1' to file to enable tracepoint
    enable_kvm_syscall = open("/sys/kernel/tracing/events/kvm/kvm_exit/enable", "w+")
    enabled = int(enable_kvm_syscall.read(1))

    if not enabled:
        enable_kvm_syscall.write("1")
        enable_kvm_syscall.close()
        
        
        
def vm_exit():
    global vm_exit_zero_counter
    global vm_exit_thirty_two_counter
    enable_tracepoint()

    trace = BPF(text="""""", cflags=["-Wno-macro-redefined"])
    
    
    while 1 and time() < end:
        try:
            (task, pid, cpu, flags, ts, msg) = trace.trace_fields()
            kvm_exit = msg.decode(errors='ignore').split()
            if kvm_exit[3] == "EXCEPTION_NMI":
                vm_exit_zero_counter += 1
            if kvm_exit[3] == "MSR_WRITE":
                vm_exit_thirty_two_counter += 1
        except ValueError:
            continue

    print("VM EXIT ZERO: " + str(vm_exit_zero_counter))
    print("VM EXIT MSR WRITE: " + str(vm_exit_thirty_two_counter))

vm_exit()