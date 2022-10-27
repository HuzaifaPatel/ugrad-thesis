#include "kvm_syscall.h"
#include "struct.h"
#include "interface.h"
struct kvm_info* kvm_info;

int main(int argc, char* argv[]){
	populate_kvm_info();
	// print_interface();
	// free_populated_kvm_info();
}