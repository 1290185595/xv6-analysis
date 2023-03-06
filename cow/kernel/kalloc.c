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
    char *ref;
} kmem;

inline int p2i(void *p) {
    return (PGROUNDUP((uint64) p) - PGROUNDUP((uint64) end)) / PGSIZE;
}

void
freerange(void *pa_start, void *pa_end) {
    char *p;
    p = (char *) PGROUNDUP((uint64) pa_start);
    for (; p + PGSIZE <= (char *) pa_end; p += PGSIZE)
        kfree(p);
}

inline int kref_change(void *pa, int i) {
    acquire(&kmem.lock);
    i = kmem.ref[p2i(pa)] += i;
    release(&kmem.lock);
    return i;
}

int kref_cnt(void *pa) {
    return kref_change(pa, 0);
}

void kref_add(void *pa) {
    kref_change(pa, 1);
}

int kref_sub(void *pa) {
    return kref_change(pa, -1);
}

void
kinit() {
    int cnt = p2i((void *) PHYSTOP);
    initlock(&kmem.lock, "kmem");

    memset(end, 1, cnt);
    acquire(&kmem.lock);
    kmem.ref = end;
    release(&kmem.lock);
    freerange(end + cnt, (void *) PHYSTOP);
}


// Free the page of physical memory pointed at by pa,
// which normally should have been returned by a
// call to kalloc().  (The exception is when
// initializing the allocator; see kinit above.)
void
kfree(void *pa) {
    struct run *r;

    if (((uint64) pa % PGSIZE) != 0 || (char *) pa < end || (uint64) pa >= PHYSTOP)
        panic("kfree");

    if (kref_sub(pa)) return;


    // Fill with junk to catch dangling refs.
    memset(pa, 1, PGSIZE);

    r = (struct run *) pa;

    acquire(&kmem.lock);
    r->next = kmem.freelist;
    kmem.freelist = r;
    release(&kmem.lock);
}

// Allocate one 4096-byte page of physical memory.
// Returns a pointer that the kernel can use.
// Returns 0 if the memory cannot be allocated.
void *
kalloc(void) {
    struct run *r;

    acquire(&kmem.lock);
    r = kmem.freelist;
    if (r)
        kmem.freelist = r->next;
    release(&kmem.lock);

    if (r)
        memset((char *) r, 5, PGSIZE); // fill with junk
    return (void *) r;
}
