#ifndef PRINT
#define PRINT
#include "struct.h"

#define MAX_USER_INPUT 32
#define BADKEY -1
#define HELP 1
#define LIST 2

void print_interface();
void list_kvm_vms();
int interpret_input(char* user_buffer);
int keyfromstring(char *key);
void list_help_dialog();

typedef struct { 
	char *key; 
	int val; 
	char* desc;} 
t_symstruct;

extern struct kvm_info* kvm_info;
#endif