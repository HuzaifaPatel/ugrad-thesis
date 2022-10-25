#include "kvm_syscall.h"
struct kvm_info* kvm_info;

int sum_vcpus(int* vcpu_running_per_vm){
	int sum = 0;

	for(int i = 0; i < kvm_info->vms_running; i++){
		sum += vcpu_running_per_vm[i];
	}

	return sum;
}	

void print_interface(){
	char* id = "ID";
	char* name = "NAME";
	char* kvm_pid = "KVM PID";
	char* temp_name = "Huzaifa Patel";

	printf("Welcome to frail, the KVM system call introspection interactive terminal.\n\n");
	printf(" %-6s %-15s %-13s", id, name, kvm_pid);

	for(int i = 0; i < find_max_vcpus(); i++){
		printf("VCPU #%d PID    ", i);
	}
	printf("\n");

	for(int dash = 0; dash < DEFAULT_DASHES; dash++){
		printf("-");
	}

	for(int dash = 0; dash < DASH_PER_VCPU * find_max_vcpus(); dash++){
		printf("-");
	}
	printf("\n");


	for(int i = 0; i < kvm_info->vms_running; i++){
		printf(" %-6d %-15s %-13d", i, temp_name, kvm_info->vm[i].pid);

		for(int j = 0; j < kvm_info->vm[i].num_vcpus; j++){
			printf("%-15d", kvm_info->vm[i].vcpu->pid);
		}
	}

	printf("\n");
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
	int* vcpu_running_per_vm;
	int* num_kvm_pid_vcpu_pid;
	int num_kvm_pid_vcpu_pid_counter = 0;

	ioctl(fd, KVM_GET_VM_SIZE, &num_kvm_vms);
	kvm_info = malloc(sizeof(struct kvm_info) * num_kvm_vms);
	kvm_info->vms_running = num_kvm_vms;
	kvm_info->vm = malloc(sizeof(struct vm) * kvm_info->vms_running);

	if(!kvm_info->vms_running){
		printf("NO KVM VMs RUNNING... EXITING\n");
		exit(-1);
	}

	vcpu_running_per_vm = malloc(sizeof(int) * kvm_info->vms_running);
	ioctl(fd, KVM_GET_VCPU_SIZE, vcpu_running_per_vm);


	
	for(int i = 0; i < kvm_info->vms_running; i++){
		kvm_info->vm[i].num_vcpus = vcpu_running_per_vm[i];
		kvm_info->vm[i].vcpu = malloc(sizeof(struct vcpu) * kvm_info->vm[i].num_vcpus);
	}

	num_kvm_pid_vcpu_pid = malloc(sizeof(int) * (kvm_info->vms_running + sum_vcpus(vcpu_running_per_vm)));
	ioctl(fd, KVM_GET_VM_VCPU_PID, num_kvm_pid_vcpu_pid);

	for(int i = 0; i < kvm_info->vms_running; i++){
		kvm_info->vm[i].pid = num_kvm_pid_vcpu_pid[num_kvm_pid_vcpu_pid_counter++];
		for(int j = 0; j < kvm_info->vm[i].num_vcpus; j++){
			kvm_info->vm[i].vcpu[j].pid = num_kvm_pid_vcpu_pid[num_kvm_pid_vcpu_pid_counter++];
		}
	}
}

// void execute_kvm_syscall_ebpf_trace()

int find_max_vcpus(){
	int max = 0;

	for(int i = 0; i < kvm_info->vms_running; i++){
		if(kvm_info->vm[i].num_vcpus > max){
			max = kvm_info->vm[i].num_vcpus;
		}
	}

	return max;
}

int find_digits(int num){

}
