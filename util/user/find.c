#include "kernel/types.h"
#include "kernel/stat.h"
#include "user/user.h"
#include "kernel/fs.h"

char* filename(char *path) {
    char *p=path+strlen(path);
    while(p >= path && *p != '/') p--;
    return p+1;
}

void find(char *path, char* target)
{
    char buf[512], *p;
    int fd;
    struct dirent de;
    struct stat st;

    if((fd = open(path, 0)) < 0){
        fprintf(2, "ls: cannot open %s\n", path);
        return;
    }

    if(fstat(fd, &st) < 0){
        fprintf(2, "ls: cannot stat %s\n", path);
        close(fd);
        return;
    }

    if (!strcmp(filename(path), target)) {
        printf("%s\n", path);
    }

    switch(st.type){
        case T_DEVICE:
        case T_FILE:
            break;

        case T_DIR:
            if(strlen(path) + 1 + DIRSIZ + 1 > sizeof buf){
                printf("ls: path too long\n");
                break;
            }
            strcpy(buf, path);
            p = buf+strlen(buf);
            *p++ = '/';
            while(read(fd, &de, sizeof(de)) == sizeof(de)){
                if(de.inum == 0) continue;
                memmove(p, de.name, DIRSIZ);
                p[DIRSIZ] = 0;
                if(stat(buf, &st) < 0){
                    printf("ls: cannot stat %s\n", buf);
                    continue;
                }
                if (strcmp(filename(buf), ".") && strcmp(filename(buf), "..")) {
                    find(buf, target);
                }
            }
            break;
    }
    close(fd);
}

int
main(int argc, char *argv[])
{
    if(argc == 2){
        find(".", argv[1]);
    } else if(argc == 3){
        printf("%s %s\n", argv[1], argv[2]);
        find(argv[1], argv[2]);
    }
    exit(0);
}
