# Additional Makefile Optimization Options
# Current Makefile already has excellent optimizations
# These are optional aggressive additions if you want to experiment further

## Current Status: ✅ EXCELLENT
Your Makefile already has:
- ✅ -march=native (CPU-specific)
- ✅ -flto (Link-time opt)
- ✅ -ffast-math (Fast FP)
- ✅ -funroll-loops
- ✅ -finline-functions
- ✅ -ftree-vectorize

## Optional Advanced Additions (if you want to experiment):

### 1. Additional Fast-Math Flags
```makefile
# Add to OPT_FLAGS:
-fno-signed-zeros -fno-trapping-math -fassociative-math -freciprocal-math
```
**Benefit:** Even more aggressive floating-point optimizations
**Risk:** May affect numerical stability (test carefully!)

### 2. Prefetch Optimizations
```makefile
# Add to OPT_FLAGS:
-fprefetch-loop-arrays
```
**Benefit:** Better cache prefetching in loops
**Expected:** 2-5% improvement for memory-bound code

### 3. Profile-Guided Optimization (Two-pass build)
```makefile
# Stage 1: Build with instrumentation
profile-generate:
	$(MAKE) clean
	$(MAKE) CXXFLAGS="$(CXXFLAGS) -fprofile-generate" \
	        LDFLAGS="$(LDFLAGS) -fprofile-generate"

# Stage 2: Run representative workload (creates .gcda files)
profile-run:
	./wireroute -f inputs/timeinput/medium_4096.txt -n 8 -i 5 -m A -b 1

# Stage 3: Build with profile data
profile-use:
	$(MAKE) clean
	$(MAKE) CXXFLAGS="$(CXXFLAGS) -fprofile-use -fprofile-correction" \
	        LDFLAGS="$(LDFLAGS) -fprofile-use"

# Complete PGO workflow
pgo: profile-generate profile-run profile-use
	@echo "Profile-guided optimization complete"
```
**Benefit:** 5-15% additional speedup
**Effort:** Requires 3-step build process

### 4. Parallel LTO Compilation
```makefile
# Add to LDFLAGS:
LDFLAGS = -flto=$(shell nproc) -fopenmp
```
**Benefit:** Faster compilation (uses all CPU cores for LTO)
**Current:** You saw "serial compilation of 5 LTRANS jobs"
**With this:** Parallel compilation

### 5. Aggressive Inlining Limits
```makefile
# Add to OPT_FLAGS:
--param inline-unit-growth=100 --param large-function-growth=1000
```
**Benefit:** More aggressive inlining
**Risk:** Larger binary, may hurt cache

### 6. OpenMP-Specific Optimizations
```makefile
# Set environment variable (not in Makefile, but for runtime):
export OMP_SCHEDULE=dynamic,1
export OMP_PROC_BIND=spread
export OMP_PLACES=cores
```
**Benefit:** Better thread scheduling and affinity
**Method:** Set in shell or in your run script

## My Recommendation: **Keep Current Makefile** ✅

Your current Makefile is **already excellent**. The optimizations you have are:
- Safe
- Effective (6.66x speedup on 8 threads!)
- Well-balanced

**Only consider additions if:**
1. You want to experiment with PGO for assignment comparison
2. You're seeing specific bottlenecks in Tracy that need targeted optimization
3. You want faster compilation (parallel LTO)

## Quick Check: What's Actually Being Used?

Run this to verify all flags:
```bash
make clean
make show-flags
make -n TRACY_ENABLED=1 | grep "^g++"
```

This shows exactly what commands are executed.

## Current Performance: **Very Good!**
```
1 thread:  33.28s (baseline)
2 threads: 17.95s (1.85x = 92.5% efficient)
4 threads:  8.88s (3.74x = 93.5% efficient)
8 threads:  4.99s (6.66x = 83.3% efficient)
```

**Conclusion:** Your Makefile optimizations are working excellently. 
No changes needed unless you want to experiment with PGO.
