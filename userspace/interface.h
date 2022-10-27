#ifndef INTERFACE
#define INTERFACE
#include "struct.h"
#include "kvm_syscall.h"
#include <readline/readline.h>
#include <readline/history.h>

#define _GNU_SOURCE 
#define MAX_USER_INPUT 32
#define BADKEY -1
#define BADOPTION -2
#define HELP 1
#define LIST 2
#define QUIT 3
#define TRACE 4
#define ONE_OPTION 1
#define MULTIPLE_OPTIONS 2

void print_interface();
void list_kvm_vms();
void interpret_input(char* user_buffer);
int keyfromstring(char *key, int argc);
void list_help_dialog();
void trace_kvm();
char** parse_arguments(char* user_buffer, int* argc);
int trace_arg_valid(int cases, int argc, char** args, char* bad_arg);
int valid_pid(int argc, char** args);

typedef struct { 
	char *key; 
	int val; 
	char* desc;
} 
t_symstruct;

extern struct kvm_info* kvm_info;
extern int* num_kvm_pid_vcpu_pid;
extern int* vcpu_running_per_vm;
#endif