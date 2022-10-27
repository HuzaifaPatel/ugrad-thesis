all: main.o kvm.o interface.o
	gcc -o main main.o kvm.o interface.o $$(pkg-config readline --cflags --libs)
main.o: main.c kvm.h interface.h
	gcc -c main.c

kvm.o: kvm.c kvm.h
	gcc -c kvm.c

interface.o: interface.c interface.h
	gcc -c interface.c

clean:
	rm -f *.o main