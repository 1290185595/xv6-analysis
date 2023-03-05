//// Physical memory allocator, for user processes,
//// kernel stacks, page-table pages,
//// and pipe buffers. Allocates whole 4096-byte pages.
//
//#include "types.h"
//#include "param.h"
//#include "memlayout.h"
//#include "spinlock.h"
//#include "riscv.h"
//#include "defs.h"
//
//void freerange(void *pa_start, void *pa_end);
//
//int pa2index(void *pa);
//
//extern char *end; // first address after kernel.
//// defined by kernel.ld.
//
//struct run {
//    struct run *next;
//};
//
//struct {
//    struct spinlock lock;
//    struct run *freelist;
//    char *pa_ref_cnt;
//} kmem;
//
//void
//kinit() {
//    initlock(&kmem.lock, "kmem");
//
//    int i = pa2index((void *) PHYSTOP);
//    acquire(&kmem.lock);
//    kmem.pa_ref_cnt = end;
//    end += i;
//    printf("kmem.pa_ref_cnt:%p, end=%p, i = %d\n", kmem.pa_ref_cnt, end, i);
//    memset(kmem.pa_ref_cnt, 1, i);
//    release(&kmem.lock);
//
//
//    freerange(end, (void *) PHYSTOP);
//}
//
//
//int pa2index(void *pa) {
//    printf("pa2index %p => %d\n", pa, (int) (((uint64) pa - PGROUNDUP((uint64) end)) >> 12));
//    return (int) (((uint64) pa - PGROUNDUP((uint64) end)) >> 12);
//}
//
//
//void
//freerange(void *pa_start, void *pa_end) {
//    char *p;
//    pa_start = (char *) PGROUNDUP((uint64) pa_start);
//
//    for (p = pa_start; p + PGSIZE <= (char *) pa_end; p += PGSIZE) {
//        kfree(p);
//    }
//}
//
//// Free the page of physical memory pointed at by pa,
//// which normally should have been returned by a
//// call to kalloc().  (The exception is when
//// initializing the allocator; see kinit above.)
//void
//kfree(void *pa) {
//    struct run *r;
//
//    if (((uint64) pa % PGSIZE) != 0 || (char *) pa < end || (uint64) pa >= PHYSTOP) {
//        panic("kfree");
//    }
//    if (--kmem.pa_ref_cnt[pa2index(pa)] == 0) {
//
//        // Fill with junk to catch dangling refs.
//        memset(pa, 1, PGSIZE);
//        r = (struct run *) pa;
//
//        acquire(&kmem.lock);
//        r->next = kmem.freelist;
//        kmem.freelist = r;
//        release(&kmem.lock);
//    }
//}
//
//void
//kkeep(void *pa) {
//    if (((uint64) pa % PGSIZE) != 0 || (char *) pa < end || (uint64) pa >= PHYSTOP) {
//        panic("kkeep");
//    }
//
//    acquire(&kmem.lock);
//    ++kmem.pa_ref_cnt[pa2index(pa)];
//    release(&kmem.lock);
//}
//
//// Allocate one 4096-byte page of physical memory.
//// Returns a pointer that the kernel can use.
//// Returns 0 if the memory cannot be allocated.
//void *
//kalloc(void) {
//    struct run *r;
//
//    acquire(&kmem.lock);
//    r = kmem.freelist;
//    if (r) {
//        kmem.freelist = r->next;
//        kmem.pa_ref_cnt[pa2index(r)] = 1;
//    }
//    release(&kmem.lock);
//
//    if (r) {
//        memset((char *) r, 5, PGSIZE); // fill with junk
//    }
//    return (void *) r;
//}








///////////////////////////////////////////////
//// Physical memory allocator, for user processes,
//// kernel stacks, page-table pages,
//// and pipe buffers. Allocates whole 4096-byte pages.
//
#include "types.h"
#include "param.h"
#include "memlayout.h"
#include "spinlock.h"
#include "riscv.h"
#include "defs.h"

void freerange(void *pa_start, void *pa_end);

extern char end[]; // first address after kernel.
// defined by kernel.ld.

struct run {
    struct run *next;
};

struct {
    struct spinlock lock;
    struct run *freelist;
} kmem;

void
kinit() {
    initlock(&kmem.lock, "kmem");
    freerange(end, (void *) PHYSTOP);
}

void kkeep(void *) {

}

void
freerange(void *pa_start, void *pa_end) {
    char *p;
    p = (char *) PGROUNDUP((uint64) pa_start);
    for (; p + PGSIZE <= (char *) pa_end; p += PGSIZE)
        kfree(p);
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
