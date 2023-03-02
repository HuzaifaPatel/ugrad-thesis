#ifndef INTERFACE
#define INTERFACE
extern struct kvm_info* kvm_info;
extern unsigned long* active_kvm_pids;
#include "struct.h"
#include "kvm.h"
#include <signal.h>
#include <readline/readline.h>
#include <readline/history.h>
#define MAX_USER_INPUT 32
#define BADKEY -1
#define BADOPTION -2
#define HELP 1
#define LIST 2
#define QUIT 3
#define TRACE 4
#define EXIT 5
#define ACTIVE 6
#define ONE_OPTION 1
#define MULTIPLE_OPTIONS 2

void print_interface();
void list_kvm_vms();
void interpret_input(char* user_buffer);
int keyfromstring(char *key, int argc);
void list_help_dialog();
char** parse_arguments(char* user_buffer, int* argc);
int trace_arg_valid(int cases, int argc, char** args);
int valid_pid(int argc, char** args);
int trace_valid_option(char** args);
int is_empty(const char *s);
void free_args();
void kill_processes();
int already_introspecting(char* pid);

typedef struct { 
	char *key; 
	int val; 
	char* desc;
} 
t_symstruct;


#endif