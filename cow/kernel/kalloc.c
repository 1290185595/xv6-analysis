// Physical memory allocator, for user processes,
// kernel stacks, page-table pages,
// and pipe buffers. Allocates whole 4096-byte pages.

#include "types.h"
#include "param.h"
#include "memlayout.h"
#include "spinlock.h"
#include "riscv.h"
#include "defs.h"

extern char end[]; // first address after kernel.
// defined by kernel.ld.

struct run {
    struct run *next;
};

struct {
    struct spinlock lock;
    struct run *freelist;
    char *keeper;
} kmem;

int pa2idx(void *pa) {
    return (PGROUNDDOWN((uint64) pa) - PGROUNDDOWN((uint64) end)) >> 12;
}


void freerange(void *pa_start, void *pa_end) {
    int i = 0;
    for (char *p = (char *) PGROUNDUP((uint64) pa_start); p < (char *) pa_end; p += PGSIZE) {
        kfree(p);
        ++i;
    }
    printf("%d, %d\n", i, pa2idx((void *) PHYSTOP));
}

void kinit() {
    int cnt = pa2idx((void *) PHYSTOP);
    initlock(&kmem.lock, "kmem");
    acquire(&kmem.lock);
    kmem.keeper = end;
    memset(end, 1, cnt);
    release(&kmem.lock);
    freerange(end + cnt, (void *) PHYSTOP);
}


void *kalloc(void) {
    struct run *r;

    acquire(&kmem.lock);
    r = kmem.freelist;
    if (r) {
        kmem.freelist = r->next;
    }
    release(&kmem.lock);

    if (r)
        memset((char *) r, 5, PGSIZE); // fill with junk
    return (void *) r;
}

void kfree(void *pa) {
    struct run *r = 0;
    if (((uint64) pa % PGSIZE) != 0 || (char *) pa < end || (uint64) pa >= PHYSTOP) panic("kfree");


    acquire(&kmem.lock);
    if (!--kmem.keeper[pa2idx(pa)]) r = (struct run *) pa;
    release(&kmem.lock);
    if (r) {
        memset(pa, 1, PGSIZE);


        acquire(&kmem.lock);
        r->next = kmem.freelist;
        kmem.freelist = r;
        release(&kmem.lock);
    }
}


void kkeep(void *) {

}