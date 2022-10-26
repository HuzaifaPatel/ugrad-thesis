#ifndef INTERFACE
#define INTERFACE
#include "struct.h"

#define MAX_USER_INPUT 32
#define BADKEY -1
#define BADOPTION -2
#define HELP 1
#define LIST 2
#define TRACE 3
#define QUIT 4
#define ONE_OPTION 1
#define MULTIPLE_OPTIONS 2

void print_interface();
void list_kvm_vms();
int interpret_input(char* user_buffer);
int keyfromstring(char *key, int argc);
void list_help_dialog();
void trace_kvm();
char** parse_arguments(char* user_buffer, int* argc);

typedef struct { 
	char *key; 
	int val; 
	char* desc;
	int max_options;
} 
t_symstruct;

extern struct kvm_info* kvm_info;
#endif