#include "kernel/types.h"
#include "kernel/stat.h"
#include "user/user.h"

void primes(int fd[]) {
    close(fd[1]);
    char buf[1];
    if (!read(fd[0], buf, 1)) exit(0);
    int tmp = fd[0];
    pipe(fd);
    int pid = fork();
    if (pid > 0) {
        close(fd[0]);
        fd[0] = tmp;
        int v = *buf;
        printf("prime %d\n", v);
        while (read(fd[0], buf, 1))
            if (*buf % v != 0)
                write(fd[1], buf, 1);
        close(fd[0]);
        close(fd[1]);
        wait(&pid);
    } else {
        close(tmp);
        primes(fd);
    }
}

int main(int argc, char *argv[]) {
    int fd[2];
    pipe(fd);
    int pid = fork();
    if (pid > 0) {
        close(fd[0]);
        for (char c = 2; c <= 35; ++c)
            write(fd[1], &c, 1);
        close(fd[1]);
        wait(0);
    } else {
        primes(fd);
    }
    exit(0);
}