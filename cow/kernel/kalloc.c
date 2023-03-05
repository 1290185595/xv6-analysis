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
    return ((PGROUNDUP((uint64) pa) - PGROUNDUP((uint64) end)) >> 12 >> sizeof (char *));
}

void kkeep(void * pa) {
//    acquire(&kmem.lock);
//    ++kmem.pa_cnt[pa2idx(pa)];
//    release(&kmem.lock);
}

void freerange(void *pa_start, void *pa_end) {
    printf("%p\n", pa_start);
    for (char *pa = (char *) PGROUNDUP((uint64) pa_start); pa < (char *) pa_end; pa += PGSIZE) {
//        acquire(&kmem.lock);
//        kmem.pa_cnt[pa2idx(pa)] = 0;
//        release(&kmem.lock);
        kfree(pa);
    }
}


void kfree(void *pa) {
    if (((uint64) pa % PGSIZE) != 0 || (char *) pa < end || (uint64) pa >= PHYSTOP) {
        panic("kfree");
    }
    struct run *r = (struct run *) pa;

    acquire(&kmem.lock);
    r->next = kmem.freelist;
    kmem.freelist = r;
    release(&kmem.lock);
    memset(pa, 1, PGSIZE);
//    if (--kmem.pa_cnt[pa2idx(pa)]) {
//        r->next = kmem.freelist;
//        kmem.freelist = r;
//        release(&kmem.lock);
//        memset(pa, 1, PGSIZE);
//    } else {
//        release(&kmem.lock);
//    }
}

void *
kalloc(void) {
    struct run *r;

    acquire(&kmem.lock);
    r = kmem.freelist;
    if (r) kmem.freelist = r->next;
    release(&kmem.lock);
    kkeep(r);
    if (r) memset((char *) r, 5, PGSIZE); // fill with junk
    return (void *) r;
}
