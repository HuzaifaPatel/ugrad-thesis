#include "kvm.h"
#include "interface.h"
#include "struct.h"
char** args;
int argc;
int exit_flag = 0;

void print_hex(const char *s)
{
  while(*s)
    printf("%02x", (unsigned int) *s++);
  printf("\n");
}

static t_symstruct lookuptable[] = {
    { "help\0",  HELP, "- find list of available commands"}, 
    { "list",  LIST, "- list running KVM VMS"},
    { "trace", TRACE, "- trace a KVM VM \n \t  options:\n \t\t  -a\n\t\t  -p <vcpu pid>"},
    { "quit",  QUIT, "- quit frail"}
};

#define NKEYS (sizeof(lookuptable)/sizeof(t_symstruct))

int is_empty(const char *s) {
  while (*s != '\0') {
    if (!isspace((unsigned char)*s))
      return 0;
    s++;
  }
  return 1;
}


int keyfromstring(char *key, int argc){
    for (int i = 0; i < NKEYS; i++) {

        t_symstruct sym = lookuptable[i];
        if (!strcmp(sym.key, key)){
            return sym.val;
    	}
    }

    return BADKEY;
}

void list_help_dialog(){
	printf("Commands:\n\n");
	for(int commands = 0; commands < NKEYS; commands++){
		printf("%5s","");
		printf("%-23s %2s\n", lookuptable[commands].key, lookuptable[commands].desc);
	}
}

void list_kvm_vms(){
	char* id = "ID";
	char* name = "NAME";
	char* kvm_pid = "KVM PID";
	char* temp_name = "Huzaifa Patel";

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
			printf("%-15d", kvm_info->vm[i].vcpu[j].pid);
		}
	}

	printf("\n");
}

char** parse_arguments(char* user_buffer, int* argc){
	char* command = strtok(user_buffer, " ");
	char** argv = NULL;

	if(command != NULL){
		argv = malloc(sizeof(char*));
		argv[*argc] = malloc(sizeof(char) * (strlen(command) + 1));
		strcpy(argv[(*argc)++], command);
	}

	while(command != NULL){
		command = strtok(NULL, " ");
		if(command != NULL){
			(*argc)++;
			argv = realloc(argv, sizeof(char*) * *argc);
			argv[*argc - 1] = malloc(sizeof(char) * (strlen(command) + 1));
			strcpy(argv[(*argc) - 1], command);
		}
	}

	return argv;
}

int valid_pid(int argc, char** args){
	int num_pids = get_sum_vcpus();
	int* valid_pid = get_only_vcpu_pid();
	long arg_pid = 0;
	char* arg_pid_remaining = NULL;
	int inputted_pids[argc - 2];

	memset(inputted_pids, 0x00, sizeof(int) * (argc - 2));

	for(int i = 2; i < argc; i++){
		for(int j = 0; j < num_pids; j++){
			arg_pid = strtol(args[i], &arg_pid_remaining, 10);
			if(valid_pid[j] == arg_pid){
				inputted_pids[i - 2] = arg_pid;
			}
		}
	}

	for(int i = 0; i < (argc - 2); i++){
		if(!inputted_pids[i])
			return 0;
	}

	return 1;
}

int trace_arg_valid(int cases, int argc, char** args){
	const char* valid_args[] = {"-a", "-p"};
	int flag = 0;

	for(int j = 0; j < sizeof(valid_args)/sizeof(valid_args[0]); j++){
		if(!strcmp(args[1], valid_args[j])){
			flag = 1;

			if(!j && argc > 2){
				printf("option -a must not be used with another option or argument");
				return 0;
			}

			if(!j && argc == 2){
				return 1;
			}

			if(j && argc <= 2){
				printf("-p must be followed by an argument");
				return 0;
			}

			if(j && argc > 2 && !valid_pid(argc, args)){
				printf("PID argument is not valid");
				return 0;
			}
		}
	}

	return 1;
}

int trace_valid_option(char** args){
	const char* valid_args[] = {"-a", "-p"};
	int flag = 0;

	for(int i = 0; i < sizeof(valid_args)/sizeof(valid_args[0]); i++){
		if(!strcmp(args[1], valid_args[i]))
			flag = 1;
	}

	return flag;
}

void interpret_input(char* user_buffer){
	argc = 0;
	
	args = parse_arguments(user_buffer, &argc);
	int cases = keyfromstring(args[0], argc);
	char* bad_arg;

	if(cases >= 1 && cases <= 3 && argc > 1){
		bad_arg = args[1];
		goto invalid_option;
	}
	switch(cases){
		case HELP:
			list_help_dialog();
			return;
		case LIST:
			list_kvm_vms();	
			return;
		case QUIT:
			printf("\n");
			exit_flag = 1;
			return;
		case TRACE:
			if(argc == 1){
				printf("trace must be used with -all or -p <vcpu pid>\nTry 'help' for more information");	
				return;
			}

			if(!trace_valid_option(args)){
				bad_arg = args[1];
				goto invalid_option;
			}

			if(!trace_arg_valid(cases, argc, args))
				return;
			
			execute_kvm_syscall_ebpf_trace(argc - 2, args + 2);
			return;
		case BADKEY:
			printf("error: unknown command: '%s'", user_buffer);
			return;

	}

	invalid_option:
		printf("invalid option: -- '%s' \nTry 'help' for more information", bad_arg);
		return;
}

void free_args(){
	for(int i = 0; i < argc; i++){
		free(args[i]);
	}

	free(args);
}

void print_interface(){
	char user_buffer[MAX_USER_INPUT];
	char* input = NULL;
	char* new_input = NULL;
	//  https://thoughtbot.com/blog/tab-completion-in-gnu-readline
	printf("Welcome to frail, the KVM system call introspection interactive terminal.\n\n");
	printf("Type:  'help' for help with commands\n");
	printf("       'quit' to quit\n\n");

	while(1){
		populate_kvm_info();
		input = readline("frail # ");

		new_input = malloc(sizeof(char) * (strlen(input) + 1));
		new_input = input;
		new_input[strlen(input)] = '\0';
		add_history(input);

		if(is_empty(new_input)){
			free_populated_kvm_info();
			free_args();
			free(new_input);
			free(input);
			rl_clear_history();
			continue;
		}

		interpret_input(new_input);

		free_populated_kvm_info();
		free_args();
		free(new_input);
		free(input);
		rl_clear_history();

		if(exit_flag)
			exit(1);

		printf("\n");
	}

}