all: main.o kvm.o interface.o
	gcc -g -o main main.o kvm.o interface.o $$(pkg-config readline --cflags --libs)
main.o: main.c kvm.h interface.h
	gcc -g -c main.c

kvm.o: kvm.c kvm.h struct.h
	gcc -g -c kvm.c

interface.o: interface.c interface.h kvm.h
	gcc -g -c interface.c

clean:
	rm -f *.o main