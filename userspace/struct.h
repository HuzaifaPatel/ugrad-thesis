#ifndef STRUCT
#define STRUCT

// info for each vcpu
struct vcpu {
	unsigned long long pid;
};

// info for each vm
struct vm {
	struct vcpu* vcpu;
	int num_vcpus;
	unsigned long long pid;
};

// info for all vms
struct kvm_info {
	int vms_running;
	struct vm* vm;
};

extern struct kvm_info* kvm_info;

#endif