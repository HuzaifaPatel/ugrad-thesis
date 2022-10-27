#ifndef KVM
#define KVM
#define KVM_GET_VM_SIZE 909
#define KVM_GET_VCPU_SIZE 910
#define KVM_GET_VM_VCPU_PID 911
#define DEFAULT_DASHES 32
#define DASH_PER_VCPU 16
#define PYTHON_FILE "kvm_syscall.py"
#define NEW_ARGS 3
#include <stdio.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <linux/kvm.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <sys/mman.h>
#include "struct.h"
#include <sys/wait.h>

int sum_vcpus(int* vcpu_running_per_vm);
void print_interface();
int open_kvm();
void close_kvm(int fd);
void populate_kvm_info();
void execute_kvm_syscall_ebpf_trace(int argc, char** args);
int find_max_vcpus();	
void safety_check();
void free_populated_kvm_info();
int* get_only_vcpu_pid();
int get_sum_vcpus();

extern struct kvm_info* kvm_info;

#endif