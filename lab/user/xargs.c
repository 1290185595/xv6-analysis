#include "kernel/types.h"
#include "kernel/stat.h"
#include "user/user.h"

#define MSGSIZE 16

int main (int argc, char *argv[]) {
    char *xargs[argc];
    char buf[MSGSIZE];
    sleep(10);
    read(0, buf, MSGSIZE);
    for (int i=1; i < argc; ++i) {
        xargs[i-1] = argv[i];
    }
    for(int n = strlen(buf), i = 0, j = 0; i < n; ++i) {
        if (buf[i] == '\n') {
            buf[i] = '\0';
        }
        if (buf[i] == '\0') {
            xargs[argc-1] = buf+j;
            j = i+1;
            int pid = fork();
            if (pid > 0) {
                wait(0);
            } else {
                exec(xargs[0], xargs);
                exit(0);
            }
        }
    }
    exit(0);
}