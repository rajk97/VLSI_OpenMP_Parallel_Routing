# Tracy-Based Runtime Optimization Workflow

## Quick Start

### 1. **Build Tracy-Enabled Binary**
```bash
cd /home/raj/Documents/Projects/PCA/VLSI_across_wire/code
make clean
make TRACY_ENABLED=1
```
Verify: Binary should be ~472KB (not 64KB)

### 2. **Collect Profiles Automatically**
```bash
./collect_tracy_profiles.sh
```
This generates traces in `tracy_profiles/` directory for:
- Inputs: easy_4096, medium_4096, hard_4096
- Threads: 1, 2, 4, 8
- Total: 12 trace files (3 inputs × 4 thread counts)

### 3. **Collect Single Profile Manually** (if needed)
```bash
# Pattern:
(/path/to/tracy-capture -o OUTPUT.tracy -f > /dev/null 2>&1 &) && \
sleep 3 && \
./wireroute -f INPUT -n THREADS -i ITERATIONS -m A -b BATCH && \
sleep 2

# Example:
(/home/raj/Documents/Projects/system_software/tracy/capture/build/tracy-capture -o test.tracy -f > /dev/null 2>&1 &) && \
sleep 3 && \
./wireroute -f inputs/timeinput/medium_4096.txt -n 4 -i 5 -m A -b 1 && \
sleep 2
```

## Analysis Workflow

### 4. **Upload and Analyze Traces**
1. Go to **https://tracy.nereid.pl/**
2. Click **"Open trace"** or drag-and-drop `.tracy` files
3. Explore different views

### 5. **Key Metrics to Examine**

#### A. **Thread Timeline View** (Main view)
- **Look for**: 
  - Load imbalance (some threads finishing much earlier)
  - Idle gaps (white space = wasted time)
  - Synchronization overhead (critical sections)
  
#### B. **Zone Statistics** (Statistics → Zones)
- **Compare**:
  - Time spent in each phase (Phase 0, Phase 1, Phase 2)
  - Critical section time (`grab_batch_critical`)
  - Expensive functions (`calculateRouteCost`, `enumerate_candidates`)
  
#### C. **Thread Comparison**
- **Check**:
  - Is work evenly distributed across threads?
  - Which thread spends most time in which zone?
  - Are threads waiting for each other?

### 6. **Comparative Analysis**

Compare traces to identify bottlenecks:

| Configuration | What to Look For |
|---------------|------------------|
| **1 thread vs 2 threads** | Is speedup close to 2x? If not, why? |
| **2 threads vs 4 threads** | Does speedup continue linearly? |
| **4 threads vs 8 threads** | Where does performance plateau? |
| **Easy vs Hard input** | How does complexity affect parallelism? |

### 7. **Optimization Questions to Answer**

Tracy will help you answer:
1. **Where is time spent?** → Zone statistics show bottleneck functions
2. **Is work balanced?** → Thread timeline shows load imbalance
3. **Synchronization cost?** → Critical section time vs total time
4. **Batch size impact?** → Compare traces with different `-b` values
5. **Scaling issues?** → Why speedup drops at high thread counts

## Common Optimization Strategies

Based on Tracy findings, consider:

### If Load Imbalance Detected:
- Adjust batch size (`-b` parameter)
- Implement dynamic work stealing
- Reorder wire processing

### If Critical Section Overhead High:
- Reduce critical section scope
- Use lock-free data structures
- Batch atomic operations

### If Phase Imbalance Detected:
- Merge phases if possible
- Pipeline phase execution
- Use better work distribution

## Example Analysis Session

```bash
# 1. Collect baseline (1 thread)
(/home/raj/Documents/Projects/system_software/tracy/capture/build/tracy-capture \
  -o tracy_profiles/baseline_t1.tracy -f > /dev/null 2>&1 &) && \
sleep 3 && \
./wireroute -f inputs/timeinput/medium_4096.txt -n 1 -i 5 -m A -b 1 && \
sleep 2

# 2. Collect parallel version (4 threads)
(/home/raj/Documents/Projects/system_software/tracy/capture/build/tracy-capture \
  -o tracy_profiles/parallel_t4.tracy -f > /dev/null 2>&1 &) && \
sleep 3 && \
./wireroute -f inputs/timeinput/medium_4096.txt -n 4 -i 5 -m A -b 1 && \
sleep 2

# 3. Compare in Tracy viewer
# - Load both traces
# - Compare total runtime
# - Check zone time differences
# - Identify parallel overhead
```

## Tips for Effective Profiling

1. **Consistent inputs**: Use same input file for comparisons
2. **Warm-up runs**: First run may have cache effects
3. **Multiple samples**: Collect 2-3 traces per configuration if results vary
4. **Focus on hotspots**: 80/20 rule - optimize the 20% taking 80% time
5. **Incremental changes**: Profile after each optimization to measure impact

## Customizing Configurations

Edit `collect_tracy_profiles.sh` to test:
- Different batch sizes: `BATCH_SIZE=1` → try 2, 4, 8
- More iterations: `SA_ITERATIONS=5` → try 10, 20
- Additional inputs: Add to `INPUTS` array
- More threads: Add to `THREADS` array (e.g., 16, 32 on PSC)

## Output

All traces saved in:
```
code/tracy_profiles/
├── easy_4096_t1.tracy
├── easy_4096_t2.tracy
├── easy_4096_t4.tracy
├── easy_4096_t8.tracy
├── medium_4096_t1.tracy
├── medium_4096_t2.tracy
└── ... (12 files total)
```

Each file: ~2-5 MB, contains complete execution trace with all instrumented zones.

## Next Steps After Analysis

1. Identify top 3 bottlenecks from Tracy
2. Hypothesize optimization strategies
3. Implement one optimization at a time
4. Re-profile to measure improvement
5. Iterate until target performance achieved

## Questions for Your Writeup

Tracy will help answer these assignment questions:
- Why can't you achieve perfect speedup?
- Where is the parallel overhead?
- How does batch size affect performance?
- Why does speedup plateau at higher thread counts?
- What is the critical path in your algorithm?
