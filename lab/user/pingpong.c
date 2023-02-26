#include "kernel/types.h"
#include "kernel/stat.h"
#include "user/user.h"
#define MSGSIZE 16
int main (int argc, char *argv[]) {
    int fd[2];
    char buf[MSGSIZE];
    pipe(fd);
    int pid = fork();
    if (pid > 0) {
        write(fd[1], "ping", MSGSIZE);
    } else {
        read(fd[0], buf, MSGSIZE);
        printf("%s", buf);
    }
    exit(0);
}