#include "kvm_syscall.h"
struct kvm_info* kvm_info;

int sum_vcpus(int vms_running, int* vcpu_running_per_vm){

}

void print_interface(){

}

int open_kvm(){
	int fd = open("/dev/kvm", O_RDONLY);

	if(fd < 0){
		printf("COULD NOT OPEN /DEV/KVM");
		exit(-1);
	}

	return fd;
}

void populate_kvm_info(){
	int fd = open_kvm();
	int num_kvm_vms;
	int* num_kvm_vcpus;
	int* num_kvm_pid_vcpu_pid;

	ioctl(fd, KVM_GET_VM_SIZE, &num_kvm_vms);
	kvm_info = malloc(sizeof(struct kvm_info) * num_kvm_vms);
	kvm_info->vms_running = num_kvm_vms;
	kvm_info->vm = malloc(sizeof(struct vm) * kvm_info->vms_running);

	if(!kvm_info->vms_running){
		printf("NO KVM VMs RUNNING... EXITING");
		exit(-1);
	}
	

	ioctl(fd, KVM_GET_VCPU_SIZE, num_kvm_vcpus);
	
	for(int i = 0; i < kvm_info->vms_running; i++){
		kvm_info->vm[i].num_vcpus = num_kvm_vcpus[i];
	}


	ioctl(fd, KVM_GET_VM_VCPU_PID, num_kvm_pid_vcpu_pid);

	for(int i = 0; i < kvm_info->vms_running; i++){
		kvm_info->vm[i].
	}
}

// void execute_kvm_syscall_ebpf_trace()

int find_max_vcpus(){

}

int find_digits(int num){

}
