#define KVM_GET_VM_SIZE 909
#define KVM_GET_VCPU_SIZE 910
#define KVM_GET_VM_VCPU_PID 911
#define DEFAULT_DASHES 32
#define DASH_PER_VCPU 16
struct kvm_info* kvm_info;
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

int sum_vcpus(int* vcpu_running_per_vm);
void print_interface();
int open_kvm();
void populate_kvm_info();
// void execute_kvm_syscall_ebpf_trace()
int find_max_vcpus();	
void safety_check();

// info for each vcpu
struct vcpu {
	int pid;
};

// info for each vm
struct vm {
	struct vcpu* vcpu;
	int num_vcpus;
	int pid;
};

// general info for all vms
struct kvm_info {
	int vms_running;
	struct vm* vm;
};