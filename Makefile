CFLAGS ?= -O3
LDFLAGS ?= -fPIC

all: searplrank.so

%.so: %.c
	${CC} ${CFLAGS} ${LDFLAGS} -shared -o $@ $?

clean:
	rm -f searplrank.so
