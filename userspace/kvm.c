#include "kvm.h"
int* vcpu_running_per_vm = NULL;
int* num_kvm_pid_vcpu_pid = NULL;

int get_sum_vcpus(){
	return sum_vcpus(vcpu_running_per_vm);
}

int sum_vcpus(int* vcpu_running_per_vm){
	int sum = 0;

	for(int i = 0; i < kvm_info->vms_running; i++){
		sum += vcpu_running_per_vm[i];
	}

	return sum;
}

int* get_only_vcpu_pid(){
	int* vcpus_pid = malloc(sizeof(int) * sum_vcpus(vcpu_running_per_vm));
	int index = 0;
	for(int i = 0; i < kvm_info->vms_running; i++){
		for(int j = 0; j < kvm_info->vm[i].num_vcpus; j++){
			vcpus_pid[index++] = kvm_info->vm[i].vcpu[j].pid;
		}
	}

	return vcpus_pid;
}

int open_kvm(){
	int fd = open("/dev/kvm", O_RDONLY);

	if(fd < 0){
		printf("COULD NOT OPEN /dev/kvm\n");
		exit(-1);
	}

	return fd;
}

void close_kvm(int fd){
	int ret = close(fd);

	if(ret){
		printf("/dev/kvm COULD NOT CLOSE\n");
		exit(-1);
	}
}

void populate_kvm_info(){
	int fd = open_kvm();
	int num_kvm_vms = 0;
	int num_kvm_pid_vcpu_pid_counter = 0;

	ioctl(fd, KVM_GET_VM_SIZE, &num_kvm_vms);
	kvm_info = malloc(sizeof(struct kvm_info));
	memset(kvm_info, 0, sizeof(struct kvm_info));
	kvm_info->vms_running = num_kvm_vms;

	if(kvm_info == NULL)
		exit(-1);

	if(!kvm_info->vms_running){
		return;
	}
	
	kvm_info->vm = malloc(sizeof(struct vm) * kvm_info->vms_running);
	memset(kvm_info->vm, 0, sizeof(struct vm) * kvm_info->vms_running);
	vcpu_running_per_vm = malloc(sizeof(int) * kvm_info->vms_running);
	memset(vcpu_running_per_vm, 0, sizeof(int) * kvm_info->vms_running);
	ioctl(fd, KVM_GET_VCPU_SIZE, vcpu_running_per_vm);
	
	for(int i = 0; i < kvm_info->vms_running; i++){
		kvm_info->vm[i].num_vcpus = vcpu_running_per_vm[i];
		kvm_info->vm[i].vcpu = malloc(sizeof(struct vcpu) * kvm_info->vm[i].num_vcpus);
	}

	num_kvm_pid_vcpu_pid = malloc(sizeof(int) * (kvm_info->vms_running + sum_vcpus(vcpu_running_per_vm)));
	memset(num_kvm_pid_vcpu_pid, 0, sizeof(int) * (kvm_info->vms_running + sum_vcpus(vcpu_running_per_vm)));
	ioctl(fd, KVM_GET_VM_VCPU_PID, num_kvm_pid_vcpu_pid);

	for(int i = 0; i < kvm_info->vms_running; i++){
		kvm_info->vm[i].pid = num_kvm_pid_vcpu_pid[num_kvm_pid_vcpu_pid_counter++];
		for(int j = 0; j < kvm_info->vm[i].num_vcpus; j++){
			kvm_info->vm[i].vcpu[j].pid = num_kvm_pid_vcpu_pid[num_kvm_pid_vcpu_pid_counter++];
		}
	}

	close_kvm(fd);
	return;
}

void execute_kvm_syscall_ebpf_trace(int argc, char** args){
	char* new_args[NEW_ARGS] = {"sudo", "python3", PYTHON_FILE};
	char** merged_args = malloc((argc + NEW_ARGS) * sizeof(char*));
	int curr_process_pid;
	int i, j;

	for(i = 0, j = 0; i < argc + NEW_ARGS; i++){
		if(i < NEW_ARGS){
			merged_args[i] = malloc(sizeof(char) * strlen(new_args[i]));
			merged_args[i] = new_args[i];
			continue;
		}

		merged_args[i] = malloc(sizeof(char) * strlen(args[j]));
		merged_args[i] = args[j++];
	}

	curr_process_pid = fork();

	if(curr_process_pid == -1)
		exit(-1);

	merged_args[argc + NEW_ARGS] = '\0';
	
	if(!curr_process_pid)
		execvp("sudo", merged_args);

	wait(&curr_process_pid);

	for(int i = NEW_ARGS; i < NEW_ARGS + argc; i++){
		free(merged_args[i]);
	}

	if(argc)
		free(merged_args);
}

void free_populated_kvm_info(){

	for(int i = 0; i < kvm_info->vms_running; i++)
		free(kvm_info->vm[i].vcpu);
		
	free(kvm_info->vm);
	free(kvm_info);
	free(num_kvm_pid_vcpu_pid);
	free(vcpu_running_per_vm);
}

int find_max_vcpus(){
	int max = 0;

	for(int i = 0; i < kvm_info->vms_running; i++){
		if(kvm_info->vm[i].num_vcpus > max)
			max = kvm_info->vm[i].num_vcpus;
	}

	return max;
}

void disable_kvm_vcpu_msr_efer_ioctl(unsigned long long pid){
	int fd = open_kvm();
	ioctl(fd, KVM_DISABLE_SCE_BIT, &pid);
	close_kvm(fd);
}
