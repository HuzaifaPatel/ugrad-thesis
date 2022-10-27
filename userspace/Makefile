all: main.o kvm_syscall.o interface.o
	gcc -o main main.o kvm_syscall.o interface.o $$( pkg-config readline --cflags --libs)
main.o: main.c kvm_syscall.h interface.h
	gcc -c main.c

kvm_syscall.o: kvm_syscall.c kvm_syscall.h
	gcc -c kvm_syscall.c

interface.o: interface.c interface.h
	gcc -c interface.c

clean:
	rm -f *.o main