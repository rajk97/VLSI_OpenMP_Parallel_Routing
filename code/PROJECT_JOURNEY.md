# VLSI Wire Routing - Project Journey Documentation

**Project**: CMU 15-418/618 Assignment 3 - Parallel VLSI Wire Routing via OpenMP  
**Student**: Raj  
**Branch**: across-wire  
**Started**: October 6, 2025  
**Last Updated**: October 18, 2025

---

## Table of Contents
1. [Initial Setup](#initial-setup)
2. [Across-Wire Implementation](#across-wire-implementation)
3. [Debugging Phase](#debugging-phase)
4. [Validation Success](#validation-success)
5. [Tracy Profiler Setup](#tracy-profiler-setup)
6. [Tracy Instrumentation](#tracy-instrumentation)
7. [Trace Collection](#trace-collection)
8. [Current Status](#current-status)

---

## Initial Setup

### Repository Structure
```
VLSI_across_wire/
├── code/
│   ├── wireroute.cpp          # Main implementation
│   ├── wireroute.h            # Header file
│   ├── Makefile               # Build configuration
│   └── inputs/                # Test inputs
└── documentation/
```

### Key Files
- **wireroute.cpp**: 396 lines, contains across-wire parallelization
- **wireroute.h**: 241 lines, data structures with forward declarations
- **Makefile**: Updated with Tracy support

---

## Across-Wire Implementation

### Algorithm Design
**Three-Phase Batching Approach:**
1. **Phase 0** (SA only): Remove old routes from occupancy
2. **Phase 1**: Find new routes with consistent occupancy snapshot
3. **Phase 2**: Update occupancy with atomic operations

### Key Implementation Details
```cpp
// Thread-local RNG (inside parallel region)
std::random_device rd; 
std::mt19937 gen(rd() + omp_get_thread_num());

// Atomic occupancy updates
#pragma omp atomic
occupancy[point.y][point.x]++;

// Critical section for batch grabbing
#pragma omp critical
{
    batch_start = batch_idx * batch_size;
    batch_idx++;
}
```

### Commands Used
```bash
# Build
cd /home/raj/Documents/Projects/PCA/VLSI_across_wire/code
make clean && make

# Run test
./wireroute -f inputs/timeinput/easy_4096.txt -n 4 -i 5 -m A -b 1

# Validate output
python3 validate.py -r routes_easy_4096_4.txt -c occupancy_easy_4096_4.txt
```

---

## Debugging Phase

### Issues Encountered and Fixed

#### Issue 1: OpenMP Pragma Syntax
**Problem**: Compiler error with `{` immediately after pragma  
**Solution**: Add newline between pragma and opening brace
```cpp
// WRONG
#pragma omp parallel {

// CORRECT
#pragma omp parallel
{
```

#### Issue 2: Phase 2 Outside Parallel Region
**Problem**: `batch_start` and `batch_end` undefined  
**Solution**: Moved Phase 2 updates inside while loop before closing brace

#### Issue 3: Missing Thread-Local RNG
**Problem**: Race conditions with shared random number generator  
**Solution**: Added thread-local RNG inside parallel regions
```cpp
std::mt19937 gen(rd() + omp_get_thread_num());
```

#### Issue 4: Header File Incomplete Type
**Problem**: Route used before full definition in Wire struct  
**Solution**: Added forward declaration
```cpp
// In wireroute.h
struct Route;  // Forward declaration at line 46
```

#### Issue 5: Output Validation Failure
**Problem**: Occupancy mismatch in validation  
**Solution**: Changed write_output to use `wire.route_path` instead of `wire.getRoutePoints()`

---

## Validation Success

### Test Results
All tests passed successfully:

```bash
# Easy test
python3 validate.py -r routes_easy_4096_4.txt -c occupancy_easy_4096_4.txt
# Result: PASS

# Medium test  
python3 validate.py -r routes_medium_4096_4.txt -c occupancy_medium_4096_4.txt
# Result: PASS

# Hard test
python3 validate.py -r routes_hard_4096_4.txt -c occupancy_hard_4096_4.txt
# Result: PASS

# Extreme test
python3 validate.py -r routes_extreme_4096_4.txt -c occupancy_extreme_4096_4.txt
# Result: PASS
```

### Git Commits
```bash
# Commit 1: Initial implementation
git add code/wireroute.cpp code/wireroute.h code/Makefile
git commit -m "Implement across-wire parallelization with three-phase batching"
git push origin across-wire

# Commit hash: 65a6ad9
```

---

## Tracy Profiler Setup

### Installation Location
```
/home/raj/Documents/Projects/system_software/tracy/
```

### Step 1: Clone Tracy
```bash
cd /home/raj/Documents/Projects/system_software
git clone https://github.com/wolfpld/tracy.git
# Result: 46,588 objects, 32.57 MiB
```

### Step 2: Install Dependencies
```bash
sudo apt-get install -y libglfw3-dev libfreetype6-dev libcapstone-dev \
                        libtbb-dev libdbus-1-dev
# Result: 20 packages, 40.2 MB disk space
```

### Step 3: Build Tracy Capture Tool
```bash
cd /home/raj/Documents/Projects/system_software/tracy/capture
mkdir -p build && cd build
cmake ..
make -j$(nproc)
# Result: SUCCESS - tracy-capture executable created
```

### Step 4: Update Project Makefile
```bash
cd /home/raj/Documents/Projects/PCA/VLSI_across_wire/code
```

**Added to Makefile:**
```makefile
# Tracy profiler configuration
TRACY_DIR = /home/raj/Documents/Projects/system_software/tracy
TRACY_ENABLED ?= 0

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

TracyClient.o: TracyClient.cpp
    $(CXX) $(CXXFLAGS) -c TracyClient.cpp
```

### Step 5: Create TracyClient.cpp
```bash
cd /home/raj/Documents/Projects/PCA/VLSI_across_wire/code
cat > TracyClient.cpp << 'EOF'
#define TRACY_ENABLE
#include "/home/raj/Documents/Projects/system_software/tracy/public/TracyClient.cpp"
EOF
```

### Step 6: Create Documentation
Created comprehensive documentation files:
- `TRACY_DOCUMENTATION.md` - Complete all-in-one guide (5,887 bytes)
- `TRACY_SETUP.md` - Detailed setup instructions
- `TRACY_COMPLETE.md` - Quick reference card
- `tracy_example.cpp` - Code instrumentation examples (3,152 bytes)

### Step 7: Commit Tracy Setup
```bash
git add code/Makefile code/TracyClient.cpp code/TRACY_*.md code/tracy_example.cpp
git commit -m "Add Tracy profiler integration and comprehensive documentation

- Updated Makefile with conditional Tracy support (TRACY_ENABLED flag)
- Added TracyClient.cpp for Tracy integration
- Created comprehensive documentation suite
- Tracy profiler installed at /home/raj/Documents/Projects/system_software/tracy
- Supports both normal and profiling builds via make flag"
# Commit hash: ac8bd3a
git push origin across-wire
```

---

## Tracy Instrumentation

### Step 1: Add Tracy Include
**File**: `wireroute.cpp`

```cpp
#include <unistd.h>
#include <omp.h>

#ifdef TRACY_ENABLE
#include "/home/raj/Documents/Projects/system_software/tracy/public/tracy/Tracy.hpp"
#endif
```

### Step 2: Instrument Key Functions

#### Main Computation Zone
```cpp
const auto compute_start = std::chrono::steady_clock::now();

#ifdef TRACY_ENABLE
  ZoneScopedN("Main Computation");
#endif
```

#### Expensive Functions
```cpp
int calculateRouteCost(...) {
#ifdef TRACY_ENABLE
  ZoneScopedN("Calculate Route Cost");
#endif
  // function body...
}

vector<Route> enumerate_candidates(...) {
#ifdef TRACY_ENABLE
  ZoneScopedN("Enumerate Candidates");
#endif
  // function body...
}
```

#### Initial Placement Parallel Region
```cpp
#pragma omp parallel
{
#ifdef TRACY_ENABLE
  ZoneScopedN("Initial Placement - Parallel Region");
#endif
  
  while(batch_idx < num_batches_default) {
#ifdef TRACY_ENABLE
    ZoneScopedN("Initial Placement - Process Batch");
#endif
    
    // Critical section
    #pragma omp critical
    {
#ifdef TRACY_ENABLE
      ZoneScopedN("Grab Batch - Critical Section");
#endif
      // batch grabbing...
    }
    
    // Phase 1
    {
#ifdef TRACY_ENABLE
      ZoneScopedN("Phase 1 - Find Initial Routes");
#endif
      // route finding...
    }
    
    // Phase 2
    {
#ifdef TRACY_ENABLE
      ZoneScopedN("Phase 2 - Update Occupancy");
#endif
      // occupancy updates...
    }
  }
}
```

#### SA Iterations
```cpp
for(int iter = 0; iter < SA_iters; ++iter) {
#ifdef TRACY_ENABLE
  ZoneScopedN("SA Iteration");
#endif
  
  #pragma omp parallel
  {
#ifdef TRACY_ENABLE
    ZoneScopedN("SA - Parallel Region");
#endif
    
    while(batch_idx < num_batches_default) {
#ifdef TRACY_ENABLE
      ZoneScopedN("SA - Process Batch");
#endif
      
      // Phase 0
      {
#ifdef TRACY_ENABLE
        ZoneScopedN("Phase 0 - Remove Old Routes");
#endif
        // removal...
      }
      
      // Phase 1
      {
#ifdef TRACY_ENABLE
        ZoneScopedN("Phase 1 - Find New Routes");
#endif
        // route finding...
      }
      
      // Phase 2
      {
#ifdef TRACY_ENABLE
        ZoneScopedN("Phase 2 - Update Occupancy");
#endif
        // occupancy updates...
      }
    }
  }
}
```

### Step 3: Build with Tracy
```bash
cd /home/raj/Documents/Projects/PCA/VLSI_across_wire/code

# Normal build (64KB)
make clean && make

# Tracy-enabled build (472KB)
make clean && make TRACY_ENABLED=1
```

**Build Results:**
- Normal binary: 66,096 bytes (64KB)
- Tracy binary: 483,328 bytes (472KB)
- Both builds successful

---

## Trace Collection

### Method: Tracy Capture Tool + Client

#### Step 1: Start Capture Tool
```bash
cd /home/raj/Documents/Projects/PCA/VLSI_across_wire/code

# Start capture in background, then run program
(/home/raj/Documents/Projects/system_software/tracy/capture/build/tracy-capture \
  -o wireroute_trace.tracy -f > /dev/null 2>&1 &) && \
sleep 3 && \
./wireroute -f inputs/timeinput/easy_4096.txt -n 4 -i 2 -m A -b 1 && \
sleep 2
```

#### Step 2: Verify Trace File
```bash
ls -lh wireroute_trace.tracy
# Output: -rw-rw-r-- 1 raj raj 3.2M Oct 18 07:50 wireroute_trace.tracy
```

**Trace File Details:**
- Location: `/home/raj/Documents/Projects/PCA/VLSI_across_wire/code/wireroute_trace.tracy`
- Size: 3.2 MB
- Contains: Profiling data from easy_4096.txt, 4 threads, 2 SA iterations
- Zones captured: ~15 instrumented zones across all phases

### Viewing Options

#### Option 1: Online Viewer (Recommended) ✅
```
Website: https://tracy.nereid.pl/
Action: Upload wireroute_trace.tracy
```

**Advantages:**
- No build required
- Always up-to-date
- Easy to use
- Perfect for analysis

#### Option 2: Local Tracy GUI (Attempted)
```bash
# Install local CMake 3.28.0
cd /home/raj/Documents/Projects/system_software
wget https://github.com/Kitware/CMake/releases/download/v3.28.0/cmake-3.28.0-linux-x86_64.tar.gz
tar -xzf cmake-3.28.0-linux-x86_64.tar.gz

# Verify
/home/raj/Documents/Projects/system_software/cmake-3.28.0-linux-x86_64/bin/cmake --version
# Output: cmake version 3.28.0

# Install missing dependencies
sudo apt-get install -y libxkbcommon-dev libwayland-dev wayland-protocols libxkbcommon-x11-dev

# Attempt to build Tracy GUI
cd /home/raj/Documents/Projects/system_software/tracy/profiler
mkdir -p build && cd build
/home/raj/Documents/Projects/system_software/cmake-3.28.0-linux-x86_64/bin/cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

**Result**: Build failed - requires GCC 13+ for C++20 `<format>` header (system has GCC 11.4)

**Decision**: Use online viewer instead (recommended approach)

---

## Current Status

### ✅ Completed
1. Across-wire parallelization implemented and validated
2. Three-phase batching algorithm working correctly
3. Thread-safe occupancy matrix updates
4. Output validation passing on all test cases
5. Code committed to GitHub (branch: across-wire, commits: 65a6ad9, ac8bd3a)
6. Tracy profiler installed and integrated
7. Tracy instrumentation added to code
8. Tracy-enabled build successful
9. Trace file collected (3.2 MB)
10. Comprehensive documentation created

### 🔄 In Progress
- Performance analysis using Tracy online viewer
- Benchmark collection across different thread counts and inputs

### 📋 Pending
- Collect full benchmark suite (1,2,4,8,16,32,64,128 threads)
- Generate multiple Tracy traces for different configurations
- Performance analysis and writeup
- Within-wire mode implementation (if required)

---

## Quick Reference Commands

### Build Commands
```bash
# Normal build
cd /home/raj/Documents/Projects/PCA/VLSI_across_wire/code
make clean && make

# Tracy-enabled build
make clean && make TRACY_ENABLED=1
```

### Run Commands
```bash
# Normal run
./wireroute -f inputs/timeinput/INPUT_FILE.txt -n THREADS -i ITERS -m A -b BATCH

# With Tracy trace collection
(/home/raj/Documents/Projects/system_software/tracy/capture/build/tracy-capture \
  -o trace_name.tracy -f > /dev/null 2>&1 &) && \
sleep 3 && \
./wireroute -f inputs/timeinput/INPUT_FILE.txt -n THREADS -i ITERS -m A -b BATCH && \
sleep 2
```

### Validation
```bash
python3 validate.py -r routes_FILE_THREADS.txt -c occupancy_FILE_THREADS.txt
```

### Git Commands
```bash
# Status
git status

# Add and commit
git add FILES
git commit -m "MESSAGE"
git push origin across-wire

# View log
git log --oneline
```

---

## File Locations

### Project Files
- **Main code**: `/home/raj/Documents/Projects/PCA/VLSI_across_wire/code/`
- **Inputs**: `/home/raj/Documents/Projects/PCA/VLSI_across_wire/code/inputs/timeinput/`
- **Outputs**: `/home/raj/Documents/Projects/PCA/VLSI_across_wire/code/` (routes_*.txt, occupancy_*.txt)

### Tracy Files
- **Tracy source**: `/home/raj/Documents/Projects/system_software/tracy/`
- **Capture tool**: `/home/raj/Documents/Projects/system_software/tracy/capture/build/tracy-capture`
- **Local CMake**: `/home/raj/Documents/Projects/system_software/cmake-3.28.0-linux-x86_64/`

### Documentation
- **Tracy docs**: `/home/raj/Documents/Projects/PCA/VLSI_across_wire/code/TRACY_DOCUMENTATION.md`
- **This file**: `/home/raj/Documents/Projects/PCA/VLSI_across_wire/code/PROJECT_JOURNEY.md`

### Trace Files
- **Current trace**: `/home/raj/Documents/Projects/PCA/VLSI_across_wire/code/wireroute_trace.tracy`

---

## Next Steps

1. **Analyze current trace** using https://tracy.nereid.pl/
2. **Generate additional traces** for different thread counts (1, 2, 4, 8)
3. **Run benchmark suite** to collect performance data
4. **Performance analysis** for assignment writeup
5. **Generate visualizations** for report

---

**End of Journey Documentation**  
*This document will be updated as the project progresses*
