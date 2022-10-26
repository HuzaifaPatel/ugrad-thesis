#include "kvm_syscall.h"
#include "struct.h"
#include "print.h"
struct kvm_info* kvm_info;

int main(){

	populate_kvm_info();
	print_interface();
}