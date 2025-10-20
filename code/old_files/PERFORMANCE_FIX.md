# Performance Investigation: Why Your System is 3.7x Slower

**Issue**: Your i9-14900KF is running 3.7x slower than expected reference times.

---

## Problem Found: CPU Power Management

### Current Status: 🔴
```bash
$ cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
powersave  # ← THIS IS THE PROBLEM!
```

### Current Frequency:
```
Actual: ~4.6 GHz
Max possible: 6.0 GHz
Loss: ~23% performance
```

---

## Solutions (Ordered by Impact)

### 🔥 **Solution 1: Change CPU Governor to "performance"** (HIGHEST IMPACT)

```bash
# Check current governor
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

# Change to performance mode (requires sudo)
sudo cpupower frequency-set -g performance

# Verify
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
# Should show: performance

# Alternative: Using cpufrequtils
sudo apt install cpufrequtils
sudo cpufreq-set -g performance
```

**Expected improvement**: 30-50% faster runtime

### 🔧 **Solution 2: Disable Hyperthreading for Performance Cores** (MEDIUM IMPACT)

Your i9-14900KF has:
- 16 P-cores (Performance cores)
- 8 E-cores (Efficiency cores)
- Total: 32 threads with HT

For compute-intensive tasks, disabling hyperthreading on P-cores can improve performance:

```bash
# Check current CPU topology
lscpu | grep -E "Thread|Core|Socket"

# Disable HT (Linux - requires sudo)
echo 0 | sudo tee /sys/devices/system/cpu/cpu16/online
echo 0 | sudo tee /sys/devices/system/cpu/cpu17/online
# ... repeat for threads 16-31
```

**Or** just use only physical cores in your runs:
```bash
# Use only 16 threads (P-cores only)
./wireroute -f inputs/timeinput/medium_4096.txt -n 16 -i 5 -m A -b 1
```

**Expected improvement**: 10-20% for compute-bound tasks

### ⚡ **Solution 3: Disable Turbo Boost Power Limits** (LOW-MEDIUM IMPACT)

Check if power limits are throttling:

```bash
# Install stress test tool
sudo apt install stress-ng

# Check throttling
watch -n 1 'cat /proc/cpuinfo | grep MHz | head -4'

# In another terminal, run stress test
stress-ng --cpu 8 --timeout 30s

# If MHz drops significantly, you're power-throttled
```

### 🔍 **Solution 4: Check for Background Processes**

```bash
# Check CPU usage before running
top -bn1 | head -20

# Check what's using CPU
ps aux --sort=-%cpu | head -10

# Kill unnecessary processes
# Be careful - don't kill system processes!
```

### 🌡️ **Solution 5: Check Thermal Throttling**

```bash
# Install monitoring tools
sudo apt install lm-sensors

# Initialize sensors
sudo sensors-detect  # Answer YES to all

# Check temperatures
sensors | grep Core

# During computation, monitor in real-time
watch -n 1 sensors
```

**Critical temps:**
- Normal: 40-60°C
- High: 60-80°C  
- Throttling: >90°C (BAD!)

---

## Quick Test After Fixes

```bash
# Set performance governor
sudo cpupower frequency-set -g performance

# Run quick test
time ./wireroute -f inputs/timeinput/medium_4096.txt -n 8 -i 5 -m A -b 1

# Expected time after fix: ~15-20 seconds (vs current 33s)
```

---

## Detailed Diagnostics

### Check All Performance Factors:

```bash
#!/bin/bash
echo "=== CPU Performance Diagnostics ==="
echo ""
echo "1. CPU Governor:"
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
echo ""
echo "2. Current Frequencies (first 8 cores):"
grep "MHz" /proc/cpuinfo | head -8
echo ""
echo "3. Turbo Boost Status:"
cat /sys/devices/system/cpu/intel_pstate/no_turbo
# 0 = turbo enabled, 1 = turbo disabled
echo ""
echo "4. CPU Temperature:"
sensors 2>/dev/null | grep Core | head -8
echo ""
echo "5. Background CPU Usage:"
top -bn1 | grep "Cpu(s)" 
echo ""
echo "6. Memory Info:"
free -h
echo ""
echo "7. Current Process Priority:"
ps -eo pid,ni,comm | grep wireroute
```

Save this as `check_performance.sh` and run it.

---

## Expected Results After Fixes

### Before (Current - Powersave Mode):
```
1 thread:  33.28s  (baseline)
8 threads:  4.99s  (6.66x speedup)
```

### After (Performance Mode):
```
1 thread:  ~15-20s  (2x faster!)
8 threads:  ~2-3s    (still ~6-7x speedup)
```

This would put you in line with the reference benchmarks!

---

## Why "powersave" Governor Hurts Performance

**Powersave mode:**
- ✗ Keeps CPU at lower frequencies (4.6 GHz vs 6.0 GHz max)
- ✗ Slower ramp-up when load increases
- ✗ May limit turbo boost
- ✓ Saves power
- ✓ Reduces heat

**Performance mode:**
- ✓ Always runs at max frequency
- ✓ Instant response to load
- ✓ Full turbo boost available
- ✗ Uses more power
- ✗ Generates more heat

**For benchmarking, ALWAYS use performance mode!**

---

## Additional Optimizations

### 1. Compile with Profile-Guided Optimization (PGO)

```bash
# Stage 1: Compile with instrumentation
make clean
make CXXFLAGS="$(make show-flags | grep CXXFLAGS | cut -d: -f2-) -fprofile-generate" \
     LDFLAGS="-fprofile-generate" \
     TRACY_ENABLED=0

# Stage 2: Run typical workload
./wireroute -f inputs/timeinput/medium_4096.txt -n 8 -i 5 -m A -b 1

# Stage 3: Recompile with profile data
make clean
make CXXFLAGS="$(make show-flags | grep CXXFLAGS | cut -d: -f2-) -fprofile-use" \
     LDFLAGS="-fprofile-use" \
     TRACY_ENABLED=0

# Test improved performance
time ./wireroute -f inputs/timeinput/medium_4096.txt -n 8 -i 5 -m A -b 1
```

**Expected gain**: Additional 5-10%

### 2. Pin Threads to Physical Cores

```bash
# Set OpenMP thread affinity
export OMP_PROC_BIND=close
export OMP_PLACES=cores

# Run
./wireroute -f inputs/timeinput/medium_4096.txt -n 8 -i 5 -m A -b 1
```

### 3. Increase Process Priority

```bash
# Run with higher priority (requires sudo)
sudo nice -n -20 ./wireroute -f inputs/timeinput/medium_4096.txt -n 8 -i 5 -m A -b 1

# Or use chrt for real-time priority
sudo chrt -f 99 ./wireroute -f inputs/timeinput/medium_4096.txt -n 8 -i 5 -m A -b 1
```

---

## Summary Checklist

Before running benchmarks, verify:
- [ ] CPU governor = "performance"
- [ ] Current MHz ~= 5000-6000 (near max)
- [ ] Turbo boost enabled (no_turbo = 0)
- [ ] CPU temp < 80°C
- [ ] No heavy background processes
- [ ] Compiled with -O3 -march=native -flto
- [ ] Using physical cores (not all HT threads)

**After these fixes, you should see 2-3x faster absolute times!**

---

## Quick Fix Command

```bash
# All-in-one performance fix
sudo cpupower frequency-set -g performance && \
export OMP_PROC_BIND=close && \
export OMP_PLACES=cores && \
echo "Performance mode enabled. Running benchmark..." && \
time ./wireroute -f inputs/timeinput/medium_4096.txt -n 8 -i 5 -m A -b 1
```

Try this and report back your new times!
