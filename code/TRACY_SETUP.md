# Tracy Profiler Setup Guide for VLSI Wire Routing Project

## Installation Summary

✅ Tracy has been installed at: `/home/raj/Documents/Projects/system_software/tracy`
✅ Your project Makefile has been updated to support Tracy
✅ `TracyClient.cpp` has been created in your code directory
✅ All required dependencies have been installed

## Quick Start

### 1. Build Your Code With Tracy

```bash
cd /home/raj/Documents/Projects/PCA/VLSI_across_wire/code

# Normal build (no profiling):
make clean && make

# Build with Tracy profiling enabled:
make clean && make TRACY_ENABLED=1
```

### 2. Add Tracy Instrumentation to wireroute.cpp

At the top of `wireroute.cpp`, after the includes, add:

```cpp
#ifdef TRACY_ENABLE
#include "tracy/public/Tracy.hpp"
#endif
```

Then wrap code sections you want to profile with Tracy zones. See `tracy_example.cpp` for detailed examples.

### 3. Run Your Program

```bash
./wireroute -f inputs/timeinput/easy_4096.txt -n 4 -i 5 -m A -b 1
```

When Tracy is enabled, this will create a trace file: `trace-XXXX.tracy` in your current directory.

### 4. View the Trace

**Option A: Online Viewer (Easiest)**
- Upload your `.tracy` file to: https://tracy.nereid.pl/
- View the timeline, thread activity, and performance metrics

**Option B: Build Tracy Profiler GUI Locally**
We need CMake 3.25+ to build the GUI. Current installed version is 3.22.1.

To upgrade CMake:
```bash
# Remove old cmake
sudo apt remove cmake

# Install newer cmake from snap
sudo snap install cmake --classic
```

Then build Tracy profiler:
```bash
cd /home/raj/Documents/Projects/system_software/tracy
mkdir -p profiler/build && cd profiler/build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

Run the profiler:
```bash
./Tracy-profiler /path/to/your/trace-XXXX.tracy
```

## What to Instrument

For your OpenMP wire routing project, focus on:

### 1. Overall Structure
- Main computation function
- SA iteration loops
- Each parallel region

### 2. Across-Wires Parallelization
- Batch grabbing (critical section)
- Phase 0: Remove old routes
- Phase 1: Find new routes
- Phase 2: Update occupancy matrix

### 3. Expensive Functions
- `enumerate_candidates()`
- `calculateRouteCost()`
- Occupancy matrix updates

## Example Instrumentation

```cpp
// In your across-wires SA loop:
for(int iter = 0; iter<SA_iters; ++iter){
    
    #pragma omp parallel
    {
#ifdef TRACY_ENABLE
        ZoneScopedN("SA Iteration");
#endif
        
        while(batch_idx < num_batches_default){
#ifdef TRACY_ENABLE
            ZoneScopedN("Process Batch");
#endif
            
            // Batch grabbing
            #pragma omp critical
            {
#ifdef TRACY_ENABLE
                ZoneScopedN("Grab Batch");
#endif
                // ... batch grabbing code ...
            }
            
            // Phase 0
            {
#ifdef TRACY_ENABLE
                ZoneScopedN("Phase 0 - Remove");
#endif
                // ... remove routes ...
            }
            
            // Phase 1
            {
#ifdef TRACY_ENABLE
                ZoneScopedN("Phase 1 - Find Routes");
#endif
                // ... find new routes ...
            }
            
            // Phase 2
            {
#ifdef TRACY_ENABLE
                ZoneScopedN("Phase 2 - Update");
#endif
                // ... update occupancy ...
            }
        }
    }
}
```

## What Tracy Will Show You

### 1. Thread Timeline
- Visual representation of what each thread is doing over time
- Easily spot idle threads (load imbalance)
- See synchronization points

### 2. Synchronization Bottlenecks
- Time spent in critical sections
- Waiting at barriers
- Lock contention

### 3. Performance Metrics
- Time spent in each zone
- Statistical summaries
- Comparative analysis across runs

### 4. Common Issues You Can Identify
- **Load Imbalance**: Some threads finish early, sit idle
- **Contention**: Threads waiting for critical section access
- **Overhead**: Too much time in batch grabbing vs actual work
- **Phase Imbalance**: One phase taking much longer than others

## Tips for Your Assignment

1. **Start Simple**: Add zones to the main parallel regions first
2. **Granularity**: Don't instrument too finely - focus on major sections
3. **Compare**: Run with different thread counts and batch sizes
4. **Analyze**: Use Tracy insights for your writeup explanations

## Troubleshooting

### Build fails with Tracy
```bash
# Make sure you're using the right flag:
make clean && make TRACY_ENABLED=1

# If still fails, check that TracyClient.cpp exists:
ls -la TracyClient.cpp
```

### No trace file generated
- Make sure you built with `TRACY_ENABLED=1`
- Check that `TRACY_ENABLE` is defined (add `-DTRACY_ENABLE` to CXXFLAGS)
- Verify `#include "tracy/public/Tracy.hpp"` is in your code

### Trace file is empty or tiny
- Add more `ZoneScoped` or `ZoneScopedN()` macros to your code
- Make sure zones are inside functions that actually execute

## Files Created

```
/home/raj/Documents/Projects/system_software/tracy/          # Tracy installation
/home/raj/Documents/Projects/PCA/VLSI_across_wire/code/
    ├── TracyClient.cpp                                      # Tracy client
    ├── tracy_example.cpp                                    # Example instrumentation
    ├── Makefile                                             # Updated with Tracy support
    └── TRACY_SETUP.md                                       # This file
```

## For Your Assignment Writeup

Tracy can help you answer questions like:
- "Why is my code unable to achieve perfect speedup?"
  → Show thread timeline with idle time, contention
  
- "Where is the synchronization overhead?"
  → Highlight time in critical sections
  
- "At high thread counts, why does performance drop off?"
  → Show increased contention, diminishing returns

Good luck with your profiling! 🚀
