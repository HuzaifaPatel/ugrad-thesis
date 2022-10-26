#include "kvm_syscall.h"
#include "interface.h"

static t_symstruct lookuptable[] = {
    { "help", HELP, "- find list of available commands", ONE_OPTION}, 
    { "list", LIST, "- list running KVM VMS", ONE_OPTION},
    { "trace", TRACE, "- trace a KVM VM \n \t  options:\n \t\t  -all\n\t\t  -pid <pid>", MULTIPLE_OPTIONS},
    { "quit", QUIT, "- quit frail", ONE_OPTION}
};



#define NKEYS (sizeof(lookuptable)/sizeof(t_symstruct))

int keyfromstring(char *key, int argc){
    int i;
    for (i = 0; i < NKEYS; i++) {

        t_symstruct sym = lookuptable[i];

        if (!strcmp(sym.key, key)){
        	if(argc > sym.max_options){
        		return BADOPTION;
        	}

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
			printf("%-15d", kvm_info->vm[i].vcpu->pid);
		}
	}

	printf("\n");
}

char** parse_arguments(char* user_buffer, int* argc){
	if(user_buffer[strlen(user_buffer) - 1] == '\n'){
			user_buffer[strlen(user_buffer) - 1] = '\0';
	}

	char* command = strtok(user_buffer, " ");
	char** argv = NULL;

	if(command != NULL){
		argv = malloc(sizeof(char*));
		argv[*argc] = malloc(sizeof(char) * strlen(command));
		strcpy(argv[(*argc)++], command);
	}

	while(command != NULL){
		command = strtok(NULL, " ");
		if(command != NULL){
			argv = realloc(argv, sizeof(char*) * (*argc));
			argv[*argc] = realloc(argv[*argc], sizeof(char) * strlen(command));
			strcpy(argv[(*argc)++], command);
		}
	}

	for(int i = 0; i < *argc; i++){
		if(argv[i][strlen(argv[i]) - 1] == '\n'){
				argv[i][strlen(argv[i]) - 1] = '\0';
		}
	}
	return argv;
}

int interpret_input(char* user_buffer){
	int argc = 0;
	char** args = parse_arguments(user_buffer, &argc);

	switch(keyfromstring(args[0], argc)){
		case HELP:
			list_help_dialog();
			break;
		case LIST:
			list_kvm_vms();
			break;
		case TRACE:
			trace_kvm();
			break;
		case QUIT:
			printf("\n");
			exit(1);
		case BADOPTION:
			printf("invalid option: -- '%s' \nTry 'help' for more information", args[1]);
		case BADKEY:
			printf("error: unknown command: '%s'", user_buffer);

	}
}

void print_interface(){
	char user_buffer[MAX_USER_INPUT];

	printf("Welcome to frail, the KVM system call introspection interactive terminal.\n\n");
	printf("Type:  'help' for help with commands\n");
	printf("       'quit' to quit\n\n");

	while(1){
		printf("frail # ");
		fgets(user_buffer, MAX_USER_INPUT, stdin);
		interpret_input(user_buffer);
		printf("\n");
	}
}



void trace_kvm(){

}