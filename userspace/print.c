#include "kvm_syscall.h"
#include "print.h"

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