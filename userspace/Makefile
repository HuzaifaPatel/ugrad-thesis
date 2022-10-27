all: main.o kvm.o interface.o
	gcc -g -o main main.o kvm.o interface.o $$(pkg-config readline --cflags --libs)
main.o: main.c kvm.h interface.h
	gcc -c -g main.c

kvm.o: kvm.c kvm.h struct.h
	gcc -c -g kvm.c

interface.o: interface.c interface.h kvm.h
	gcc -c -g interface.c

clean:
	rm -f *.o main