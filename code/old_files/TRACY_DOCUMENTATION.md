# Tracy Profiler - Complete Setup and Usage Guide

**Installation Date**: October 9, 2025  
**Installation Location**: `/home/raj/Documents/Projects/system_software/tracy`  
**Project**: VLSI Wire Routing - OpenMP Parallelization  
**Status**: ✅ FULLY OPERATIONAL

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation Summary](#installation-summary)
3. [Building Your Project](#building-your-project)
4. [Adding Instrumentation](#adding-instrumentation)
5. [Running and Collecting Traces](#running-and-collecting-traces)
6. [Viewing Traces](#viewing-traces)
7. [What to Instrument](#what-to-instrument)
8. [Understanding Tracy Output](#understanding-tracy-output)
9. [Troubleshooting](#troubleshooting)
10. [For Your Assignment](#for-your-assignment)

---

## Quick Start

### 30-Second Setup

```bash
cd /home/raj/Documents/Projects/PCA/VLSI_across_wire/code

# 1. Build with Tracy
make clean && make TRACY_ENABLED=1

# 2. Add Tracy zones to wireroute.cpp (see examples below)

# 3. Rebuild
make clean && make TRACY_ENABLED=1

# 4. Run
./wireroute -f inputs/timeinput/easy_4096.txt -n 4 -i 5 -m A -b 1

# 5. View trace at https://tracy.nereid.pl/
```

---

## Installation Summary

### What Was Installed

✅ **Tracy Source Code**
- Location: `/home/raj/Documents/Projects/system_software/tracy`
- Version: Latest from GitHub (October 2025)
- Size: ~33 MB

✅ **System Dependencies**
```
libglfw3-dev       - Graphics library for Tracy GUI
libfreetype6-dev   - Font rendering
libcapstone-dev    - Disassembly framework
libtbb-dev         - Intel Threading Building Blocks
libdbus-1-dev      - D-Bus development files
```

✅ **Project Integration**
- Modified: `Makefile` - Added Tracy build configuration
- Created: `TracyClient.cpp` - Tracy integration file
- Created: `tracy_example.cpp` - Code examples
- Created: `TRACY_SETUP.md` - Setup guide
- Created: `TRACY_COMPLETE.md` - Quick reference
- Created: `TRACY_DOCUMENTATION.md` - This comprehensive guide

### File Structure

```
/home/raj/Documents/Projects/system_software/
└── tracy/
    ├── public/              # Tracy public API
    │   ├── Tracy.hpp        # Main header (include this)
    │   └── TracyClient.cpp  # Client implementation
    ├── profiler/            # Tracy profiler GUI (needs CMake 3.25+)
    ├── manual/              # Documentation
    └── examples/            # Example programs

/home/raj/Documents/Projects/PCA/VLSI_across_wire/code/
├── TracyClient.cpp          # Your Tracy integration file
├── tracy_example.cpp        # Usage examples
├── TRACY_DOCUMENTATION.md   # This file
├── Makefile                 # Updated with Tracy support
└── wireroute.cpp            # Your code (add instrumentation here)
```

---

## Building Your Project

### Without Tracy (Normal Build)

```bash
cd /home/raj/Documents/Projects/PCA/VLSI_across_wire/code
make clean && make
```

This builds your program as usual, with no profiling overhead.

### With Tracy (Profiling Enabled)

```bash
cd /home/raj/Documents/Projects/PCA/VLSI_across_wire/code
make clean && make TRACY_ENABLED=1
```

This builds with:
- Tracy profiling enabled (`-DTRACY_ENABLE`)
- Tracy include paths added
- Tracy client library linked
- ~400KB larger binary size

### Makefile Configuration

Your Makefile has been updated with:

```makefile
# Tracy profiler configuration
TRACY_DIR = /home/raj/Documents/Projects/system_software/tracy
TRACY_ENABLED ?= 0

# Conditional Tracy flags
ifeq ($(TRACY_ENABLED), 1)
    OBJS += TracyClient.o
    TRACY_FLAGS = -DTRACY_ENABLE -I$(TRACY_DIR)/public
    TRACY_LIBS = -lpthread -ldl
else
    TRACY_FLAGS =
    TRACY_LIBS =
endif

CXXFLAGS = ... $(TRACY_FLAGS)
LDFLAGS = ... $(TRACY_LIBS)
```

---

## Adding Instrumentation

### Step 1: Include Tracy Header

At the **top** of `wireroute.cpp`, after all other includes:

```cpp
#include "wireroute.h"
#include <algorithm>
#include <iostream>
// ... other includes ...

// Add Tracy include (wrapped in ifdef)
#ifdef TRACY_ENABLE
#include "tracy/public/Tracy.hpp"
#endif
```

### Step 2: Add Zone Macros

Tracy uses "zones" to mark code sections. Each zone measures execution time.

#### Basic Zone (Automatic Function Name)

```cpp
void myFunction() {
#ifdef TRACY_ENABLE
    ZoneScoped;  // Automatically uses function name
#endif
    
    // Your code here...
}
```

#### Named Zone (Custom Name)

```cpp
{
#ifdef TRACY_ENABLE
    ZoneScopedN("My Custom Section");
#endif
    
    // Your code here...
}
```

#### Conditional Zones (Use Sparingly)

```cpp
#ifdef TRACY_ENABLE
if (condition) {
    ZoneScopedN("Conditional Path");
    // code...
}
#endif
```

### Step 3: Instrument Your OpenMP Code

#### Example 1: Main Computation

```cpp
int main(int argc, char *argv[]) {
    // ... initialization ...
    
    const auto compute_start = std::chrono::steady_clock::now();

#ifdef TRACY_ENABLE
    ZoneScopedN("Main Computation");
#endif

    if (parallel_mode == 'A') {
        // Across-wires parallelization
        // ... your code ...
    }
    
    const double compute_time = ...;
}
```

#### Example 2: Across-Wires Initial Placement

```cpp
// Phase 1: Initial placement with batching 
#pragma omp parallel
{
#ifdef TRACY_ENABLE
    ZoneScopedN("Initial Placement - Parallel Region");
#endif

    while(batch_idx < num_batches_default) {
#ifdef TRACY_ENABLE
        ZoneScopedN("Process Batch");
#endif

        int batch_start, batch_end; 
        
        // Grab a batch 
        #pragma omp critical
        {
#ifdef TRACY_ENABLE
            ZoneScopedN("Grab Batch - Critical Section");
#endif
            batch_start = (batch_idx) * batch_size; 
            batch_idx++;
            batch_end = std::min(batch_start + batch_size - 1, num_wires - 1);
        }
        
        // Phase 1: Find routes
        {
#ifdef TRACY_ENABLE
            ZoneScopedN("Phase 1 - Find Routes");
#endif
            for(int wire_idx = batch_start; wire_idx<=batch_end; wire_idx++) {
                // ... route finding code ...
            }
        }
        
        // Phase 2: Update occupancy
        {
#ifdef TRACY_ENABLE
            ZoneScopedN("Phase 2 - Update Occupancy");
#endif
            for(int wire_idx = batch_start; wire_idx<=batch_end; ++wire_idx) {
                for(const auto& point: wires[wire_idx].route_path) {
                    #pragma omp atomic
                    occupancy[point.y][point.x]++;
                }
            }
        }
    }
}
```

#### Example 3: SA Iterations

```cpp
for(int iter = 0; iter < SA_iters; ++iter) {
#ifdef TRACY_ENABLE
    ZoneScopedN("SA Iteration");
#endif
    
    std::cout << "SA Iteration " << (iter+1) << "/" << SA_iters << std::endl; 
    
    int batch_idx = 0; 
    
    #pragma omp parallel
    {
#ifdef TRACY_ENABLE
        ZoneScopedN("SA Parallel Region");
#endif
        
        std::random_device rd; 
        std::mt19937 gen(rd() + omp_get_thread_num());
        std::uniform_real_distribution<> prob_dist(0.0, 1.0);
        
        while(batch_idx < num_batches_default) {
#ifdef TRACY_ENABLE
            ZoneScopedN("SA Batch");
#endif
            
            // ... batch processing with phases 0, 1, 2 ...
        }
    }
}
```

#### Example 4: Expensive Functions

```cpp
int calculateRouteCost(const Route& route, 
                       const std::vector<std::vector<int>>& occupancy) {
#ifdef TRACY_ENABLE
    ZoneScopedN("Calculate Route Cost");
#endif
    
    auto all_points = route.getAllPoints(occupancy[0].size(), occupancy.size());
    int incremental_cost = 0; 
    
    for(const auto& point: all_points) {
        int current_occupancy = occupancy[point.y][point.x];
        int old_cost = current_occupancy * current_occupancy;
        int new_cost = (current_occupancy + 1) * (current_occupancy + 1);
        incremental_cost += (new_cost - old_cost);
    }
    
    return incremental_cost;
}
```

### Best Practices

✅ **DO:**
- Wrap major code sections (parallel regions, phases, expensive functions)
- Use descriptive names: `"Phase 1 - Find Routes"` not just `"Phase 1"`
- Keep zones around relatively coarse-grained operations
- Always wrap Tracy code in `#ifdef TRACY_ENABLE`

❌ **DON'T:**
- Instrument every single line (too much overhead)
- Put zones inside tight loops (millions of iterations)
- Forget the `#ifdef` guards (will break normal builds)
- Use zones for trivial operations (< 1 microsecond)

---

## Running and Collecting Traces

### Running Your Program

```bash
# With Tracy enabled:
./wireroute -f inputs/timeinput/easy_4096.txt -n 4 -i 5 -m A -b 1

# You'll see normal output plus:
# Tracy trace saved to: trace-20251009-064523.tracy
```

### Trace File Information

- **Format**: `.tracy` binary format
- **Location**: Current working directory
- **Naming**: `trace-YYYYMMDD-HHMMSS.tracy`
- **Size**: Varies (typically 1-100 MB depending on program length and instrumentation)

### Running Multiple Experiments

```bash
# Different thread counts
for threads in 1 2 4 8; do
    ./wireroute -f inputs/timeinput/easy_4096.txt -n $threads -i 5 -m A -b 1
    mv trace-*.tracy trace_easy_${threads}threads.tracy
done

# Different batch sizes
for batch in 1 5 10 20; do
    ./wireroute -f inputs/timeinput/medium_4096.txt -n 8 -i 5 -m A -b $batch
    mv trace-*.tracy trace_medium_batch${batch}.tracy
done
```

---

## Viewing Traces

### Option 1: Online Viewer (Recommended)

**Website**: https://tracy.nereid.pl/

**Steps**:
1. Go to https://tracy.nereid.pl/
2. Click "Choose File" or drag-and-drop your `.tracy` file
3. Wait for upload and processing
4. Explore the trace!

**Advantages**:
- ✅ No local setup needed
- ✅ Always up-to-date
- ✅ Works immediately

**Disadvantages**:
- ❌ Requires internet
- ❌ File size limits (typically < 100 MB)
- ❌ Privacy concerns for sensitive data

### Option 2: Local Tracy Profiler GUI

**Requirements**:
- CMake 3.25 or higher (current system has 3.22.1)
- Build tools and dependencies (already installed)

**Upgrade CMake** (if needed):

```bash
# Remove old cmake
sudo apt remove cmake

# Install newer cmake from snap
sudo snap install cmake --classic

# Verify
cmake --version  # Should show 3.25+
```

**Build Tracy Profiler**:

```bash
cd /home/raj/Documents/Projects/system_software/tracy
mkdir -p profiler/build && cd profiler/build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

**Run Tracy Profiler**:

```bash
cd /home/raj/Documents/Projects/system_software/tracy/profiler/build
./Tracy-profiler /path/to/your/trace-XXXX.tracy
```

**Advantages**:
- ✅ No internet needed
- ✅ No file size limits
- ✅ Full-featured (capture live, compare traces)
- ✅ Keeps data private

**Disadvantages**:
- ❌ Requires CMake upgrade
- ❌ More complex setup

---

## What to Instrument

### For Your Assignment: Recommended Instrumentation Points

#### 1. High-Level Structure

```cpp
// Main computation section
#ifdef TRACY_ENABLE
    ZoneScopedN("Main Computation");
#endif

// Initial placement
#ifdef TRACY_ENABLE
    ZoneScopedN("Initial Wire Placement");
#endif

// SA iterations loop
for(int iter = 0; iter < SA_iters; ++iter) {
#ifdef TRACY_ENABLE
    ZoneScopedN("SA Iteration");
#endif
}
```

#### 2. Parallel Regions

```cpp
#pragma omp parallel
{
#ifdef TRACY_ENABLE
    ZoneScopedN("Parallel Region - Initial Placement");
#endif
    // ... parallel code ...
}
```

#### 3. Synchronization Points

```cpp
// Critical sections
#pragma omp critical
{
#ifdef TRACY_ENABLE
    ZoneScopedN("Critical - Batch Grab");
#endif
    // ... batch grabbing ...
}

// Atomic updates (zone AROUND the loop, not for each atomic)
{
#ifdef TRACY_ENABLE
    ZoneScopedN("Atomic Updates - Phase 2");
#endif
    for(...) {
        #pragma omp atomic
        occupancy[point.y][point.x]++;
    }
}
```

#### 4. Three Phases

```cpp
// Phase 0: Remove
{
#ifdef TRACY_ENABLE
    ZoneScopedN("Phase 0 - Remove Old Routes");
#endif
    // ... removal code ...
}

// Phase 1: Find
{
#ifdef TRACY_ENABLE
    ZoneScopedN("Phase 1 - Find New Routes");
#endif
    // ... route finding ...
}

// Phase 2: Update
{
#ifdef TRACY_ENABLE
    ZoneScopedN("Phase 2 - Update Occupancy");
#endif
    // ... occupancy updates ...
}
```

#### 5. Expensive Functions

```cpp
// Route cost calculation
int calculateRouteCost(...) {
#ifdef TRACY_ENABLE
    ZoneScopedN("Calculate Route Cost");
#endif
    // ...
}

// Route enumeration
vector<Route> enumerate_candidates(...) {
#ifdef TRACY_ENABLE
    ZoneScopedN("Enumerate Candidates");
#endif
    // ...
}
```

---

## Understanding Tracy Output

### Tracy UI Overview

When you open a trace in Tracy, you'll see:

1. **Timeline View** (top)
   - Horizontal timeline showing program execution
   - Each thread has its own row
   - Colored bars represent zones

2. **Statistics Panel** (bottom)
   - Zone names
   - Total time, mean time, min/max
   - Call count

3. **Thread Activity**
   - Shows when each thread is active/idle
   - Visualizes load balance

### What to Look For

#### 1. Load Imbalance

**Visual**: Some thread rows end early, showing large gaps

```
Thread 0: ████████████████░░░░░░░░  <- finishes early (idle)
Thread 1: ████████████████████████  <- keeps working
Thread 2: ██████████░░░░░░░░░░░░░░  <- finishes early
Thread 3: ████████████████████████  <- keeps working
```

**Indicates**: Poor work distribution, some wires taking much longer

**Solutions**: Better load balancing, smaller batch sizes

#### 2. Synchronization Overhead

**Visual**: Many threads waiting at critical section

```
Thread 0: ████▓▓████▓▓████▓▓  <- gray = waiting
Thread 1: ▓▓████▓▓████▓▓████
Thread 2: ████▓▓████▓▓████▓▓
Thread 3: ▓▓████▓▓████▓▓████
```

**Indicates**: Too much contention, critical section is bottleneck

**Solutions**: Reduce critical section size, use atomic operations

#### 3. Phase Imbalance

**Visual**: One phase much longer than others

```
Phase 0: ██              <- short
Phase 1: ████████████    <- very long
Phase 2: ██              <- short
```

**Indicates**: Unequal work across phases

**Solutions**: Optimize expensive phase, consider different algorithm

#### 4. Thread Creation Overhead

**Visual**: Delay before threads start working

```
Time -->  [gap]████████████
          [gap]████████████
          [gap]████████████
          ^--- idle time before work starts
```

**Indicates**: OpenMP thread creation overhead

**Solutions**: Reuse parallel regions, minimize parallel region count

---

## Troubleshooting

### Build Issues

#### Error: "Tracy.hpp: No such file or directory"

**Cause**: TRACY_ENABLE defined but header not found

**Solution**:
```bash
# Check include path in Makefile
grep TRACY_FLAGS Makefile
# Should show: -I/home/raj/Documents/Projects/system_software/tracy/public

# Verify Tracy is installed
ls /home/raj/Documents/Projects/system_software/tracy/public/Tracy.hpp
```

#### Error: "undefined reference to Tracy functions"

**Cause**: Not linking Tracy client

**Solution**:
```bash
# Make sure you're using TRACY_ENABLED=1
make clean && make TRACY_ENABLED=1

# Check that TracyClient.o is built
ls -la TracyClient.o
```

#### Warning: "TRACY_ENABLE" redefined

**Cause**: Harmless - TRACY_ENABLE defined twice (Makefile + TracyClient.cpp)

**Solution**: Ignore this warning, or remove from TracyClient.cpp

### Runtime Issues

#### No trace file generated

**Cause**: Program didn't run to completion, or no zones instrumented

**Solution**:
1. Check program completes successfully
2. Verify you added Tracy zones to your code
3. Rebuild with `TRACY_ENABLED=1`
4. Check for `.tracy` files: `ls -lh *.tracy`

#### Trace file is very small (< 1KB)

**Cause**: No instrumentation or program crashed early

**Solution**:
1. Verify Tracy zones are in code that actually executes
2. Check program output for errors
3. Add more zones to capture activity

#### Program runs much slower with Tracy

**Cause**: Normal - profiling has overhead

**Expected**: 5-20% slowdown  
**If > 50%**: Too many zones, reduce instrumentation granularity

### Viewing Issues

#### Online viewer shows "File too large"

**Solution**: 
- Use shorter program runs
- Reduce number of SA iterations
- Build local Tracy profiler

#### Trace looks empty or has no zones

**Cause**: Instrumentation not compiled in

**Solution**:
```bash
# Verify TRACY_ENABLE is defined
make clean && make TRACY_ENABLED=1 2>&1 | grep TRACY_ENABLE
# Should see: -DTRACY_ENABLE

# Check that zones are in your code
grep "ZoneScoped" wireroute.cpp
```

---

## For Your Assignment

### Using Tracy for Your Writeup

Tracy will help you answer these writeup questions:

#### Question 1: "Why is your code unable to achieve perfect speedup?"

**What to measure**:
- Thread timeline to see idle time
- Critical section time vs computation time
- Load balance across threads

**Tracy screenshots to include**:
- Timeline showing thread activity
- Statistics showing time breakdown
- Comparison: 2 threads vs 8 threads

**Example findings**:
- "Thread 0 and 1 finish 30% faster than threads 6-7, indicating load imbalance"
- "Critical section accounts for 15% of total time at 8 threads"
- "Only 6.5x speedup on 8 threads due to synchronization overhead"

#### Question 2: "Where is the synchronization in your solution?"

**What to measure**:
- Time in critical sections
- Time in atomic operations
- Barrier waiting time

**Tracy zones to add**:
```cpp
#pragma omp critical
{
#ifdef TRACY_ENABLE
    ZoneScopedN("Sync - Batch Grab");
#endif
}

{
#ifdef TRACY_ENABLE
    ZoneScopedN("Sync - Atomic Updates");
#endif
    for(...) {
        #pragma omp atomic
        occupancy[y][x]++;
    }
}
```

**Example findings**:
- "Batch grabbing (critical section) takes 12% of parallel region time"
- "Atomic updates in Phase 2 take 25% of batch processing time"

#### Question 3: "At high thread counts, do you observe a drop-off?"

**What to measure**:
- Speedup curve from Tracy timings
- Contention at high thread counts
- Time waiting vs working

**Experiments to run**:
```bash
for threads in 1 2 4 8 16 32; do
    ./wireroute -f inputs/timeinput/medium_4096.txt \
                -n $threads -i 5 -m A -b 1
    mv trace-*.tracy trace_threads_${threads}.tracy
done
```

**Tracy analysis**:
- Compare timeline density at different thread counts
- Measure critical section contention
- Show thread utilization percentage

**Example findings**:
- "At 16+ threads, critical section becomes bottleneck"
- "Thread utilization drops from 95% (8 threads) to 70% (32 threads)"
- "Speedup plateaus at 16 threads due to memory bandwidth limits"

### Recommended Tracy-Based Experiments

#### Experiment 1: Batch Size Sensitivity

```bash
for batch in 1 5 10 20 50; do
    ./wireroute -f inputs/timeinput/hard_4096.txt \
                -n 8 -i 5 -m A -b $batch
    mv trace-*.tracy trace_batch_${batch}.tracy
done
```

**Compare in Tracy**:
- Phase 1 time vs batch size
- Phase 2 time vs batch size  
- Critical section overhead vs batch size

#### Experiment 2: Problem Size Scaling

```bash
for input in easy medium hard extreme; do
    ./wireroute -f inputs/timeinput/${input}_4096.txt \
                -n 8 -i 5 -m A -b 10
    mv trace-*.tracy trace_size_${input}.tracy
done
```

**Compare in Tracy**:
- Does parallel efficiency change with problem size?
- Where does time go for different input sizes?

#### Experiment 3: Thread Scaling

```bash
for threads in 1 2 4 8 16; do
    ./wireroute -f inputs/timeinput/medium_4096.txt \
                -n $threads -i 5 -m A -b 10
    mv trace-*.tracy trace_scale_${threads}.tracy
done
```

**Compare in Tracy**:
- How does load balance change with thread count?
- When does synchronization become dominant?

### Creating Visualizations for Report

1. **Thread Timeline Screenshot**
   - Zoom to show 2-3 SA iterations
   - Highlight different phases with colors
   - Show thread IDs clearly

2. **Statistics Table Screenshot**
   - Sort by total time
   - Show top 5-10 zones
   - Include call counts

3. **Comparison Screenshot**
   - Open two traces side-by-side (if using local GUI)
   - Or create table comparing metrics

4. **Annotated Diagrams**
   - Export Tracy screenshots
   - Add arrows and labels in image editor
   - Explain what you're showing

---

## Additional Resources

### Tracy Documentation

- **GitHub**: https://github.com/wolfpld/tracy
- **Manual** (PDF): Check latest releases page
- **Video Tutorial**: Search "Tracy Profiler tutorial" on YouTube

### OpenMP + Tracy

- Tracy works great with OpenMP
- Each OpenMP thread shows as separate row in timeline
- Use thread names for clarity:
  ```cpp
  #ifdef TRACY_ENABLE
      tracy::SetThreadName("Worker Thread");
  #endif
  ```

### Getting Help

1. **Tracy GitHub Issues**: https://github.com/wolfpld/tracy/issues
2. **Tracy Discord**: Link usually in README
3. **Your setup files**:
   - `TRACY_SETUP.md` - detailed setup
   - `tracy_example.cpp` - code examples
   - This file - comprehensive guide

---

## Quick Reference Card

### Build Commands

```bash
# Normal build
make clean && make

# Tracy build
make clean && make TRACY_ENABLED=1
```

### Basic Instrumentation Pattern

```cpp
#ifdef TRACY_ENABLE
#include "tracy/public/Tracy.hpp"
#endif

void myFunction() {
#ifdef TRACY_ENABLE
    ZoneScopedN("My Function");
#endif
    // code...
}
```

### Common Zones for Your Project

```cpp
// Parallel region
#pragma omp parallel {
#ifdef TRACY_ENABLE
    ZoneScopedN("Parallel Region");
#endif
}

// Critical section
#pragma omp critical {
#ifdef TRACY_ENABLE
    ZoneScopedN("Critical Section");
#endif
}

// Phase
{
#ifdef TRACY_ENABLE
    ZoneScopedN("Phase 1");
#endif
}
```

### Viewing Traces

- **Online**: https://tracy.nereid.pl/
- **Local**: `./Tracy-profiler trace-XXXX.tracy`

---

## Checklist for Your Assignment

Before submitting, make sure you:

- [ ] Added Tracy zones to key code sections
- [ ] Built with `TRACY_ENABLED=1`
- [ ] Collected traces for different configurations
- [ ] Viewed traces and identified bottlenecks
- [ ] Created screenshots/visualizations for report
- [ ] Explained findings with Tracy evidence
- [ ] Compared across-wires performance with Tracy insights
- [ ] Answered "why not perfect speedup?" using Tracy data

---

## Version Information

- **Tracy Version**: Latest (October 2025)
- **Installation Date**: October 9, 2025
- **Project**: VLSI Wire Routing OpenMP
- **Platform**: Ubuntu 22.04, GCC, OpenMP
- **Documentation Version**: 1.0

---

**End of Tracy Documentation**

For questions or issues, refer to:
- Tracy GitHub: https://github.com/wolfpld/tracy
- This documentation: `TRACY_DOCUMENTATION.md`
- Quick reference: `TRACY_COMPLETE.md`
- Setup guide: `TRACY_SETUP.md`
- Code examples: `tracy_example.cpp`

Happy profiling! 🚀
