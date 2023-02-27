#include "kernel/param.h"
#include "kernel/types.h"
#include "kernel/stat.h"
#include "user/user.h"

int main (int argc, char *argv[]) {
    if (argc < 3 || argv[1][0] < '0' || argv[1][0] > '9') {
        fprintf(2, "Usage: %s mask command\n", argv[0]);
        exit(1);
    }
    if (trace(atoi(argv[1])) < 0) {
        fprintf(2, "%s trace failed\n", argv[0]);
        exit(1);
    }
    argv+=2;
    exec(argv[0], argv);
    exit(0);
}