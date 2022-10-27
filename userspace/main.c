#include "kvm.h"
#include "struct.h"
#include "interface.h"
struct kvm_info* kvm_info = NULL;

int main(int argc, char* argv[]){
	fflush(stdout);
	print_interface();
}