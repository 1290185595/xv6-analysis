#include "types.h"
#include "param.h"
#include "memlayout.h"
#include "spinlock.h"
#include "riscv.h"
#include "defs.h"

void freerange(void *pa_start, void *pa_end);

int pa2idx(void *pa);

extern char end[]; // first address after kernel.
// defined by kernel.ld.

struct run {
    struct run *next;
};

struct {
    struct spinlock lock;
    struct run *freelist;
    char *end;
    char *pa_cnt;
} kmem;

void
kinit() {
    kmem.pa_cnt = end;
    initlock(&kmem.lock, "kmem");
    freerange(end + pa2idx((void *) PHYSTOP), (void *) PHYSTOP);
}

int pa2idx(void *pa) {
    return ((PGROUNDUP((uint64) pa) - PGROUNDUP((uint64) end)) >> 12);
}

void kkeep(void * pa) {
    acquire(&kmem.lock);
    ++kmem.pa_cnt[pa2idx(pa)];
    release(&kmem.lock);
}

void freerange(void *pa_start, void *pa_end) {
    for (char *pa = (char *) PGROUNDUP((uint64) pa_start); pa < (char *) pa_end; pa += PGSIZE) {
        acquire(&kmem.lock);
        kmem.pa_cnt[pa2idx(pa)] = 1;
        kfree(pa);
        release(&kmem.lock);
    }
}


void kfree(void *pa) {
    if (((uint64) pa % PGSIZE) != 0 || (char *) pa < end || (uint64) pa >= PHYSTOP) {
        panic("kfree");
    }
    struct run *r = (struct run *) pa;
    acquire(&kmem.lock);
    if (--kmem.pa_cnt[pa2idx(pa)] == 0) {
        r->next = kmem.freelist;
        kmem.freelist = r;
        release(&kmem.lock);
        memset(pa, 1, PGSIZE);
    } else {
        release(&kmem.lock);
    }
}

// Allocate one 4096-byte page of physical memory.
// Returns a pointer that the kernel can use.
// Returns 0 if the memory cannot be allocated.
void *
kalloc(void) {
    struct run *r;

    acquire(&kmem.lock);
    r = kmem.freelist;
    if (r) {
        kmem.freelist = r->next;
    }
    release(&kmem.lock);
    kkeep(r);
    if (r) {
        memset((char *) r, 5, PGSIZE); // fill with junk
    }
    return (void *) r;
}
