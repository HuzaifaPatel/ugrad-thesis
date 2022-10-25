all: main.o kvm_syscall.o
	gcc -o main main.o kvm_syscall.o 

main.o: main.c
	gcc -c main.c

kvm_syscall.o: kvm_syscall.c kvm_syscall.h
	gcc -c kvm_syscall.c

clean:
	rm -f *.o main