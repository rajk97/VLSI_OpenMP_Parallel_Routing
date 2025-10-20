#!/bin/bash

# Performance Mode Benchmark with Optimized Settings
# Using: performance governor + thread affinity

export OMP_PROC_BIND=close
export OMP_PLACES=cores

INPUT="inputs/timeinput/medium_4096.txt"
THREADS_LIST=(1 2 4 8)
ITERATIONS=5
BATCH=1

RESULTS_DIR="results/performance_mode"
mkdir -p "$RESULTS_DIR"

echo "=== Performance Mode Benchmark ==="
echo "CPU Governor: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)"
echo "Thread Affinity: OMP_PROC_BIND=close, OMP_PLACES=cores"
echo ""

RESULTS_FILE="${RESULTS_DIR}/speedup_comparison.txt"

{
    echo "Performance Mode Benchmark Results"
    echo "Date: $(date)"
    echo "CPU Governor: performance"
    echo "Thread Affinity: OMP_PROC_BIND=close, OMP_PLACES=cores"
    echo "=========================================="
    echo ""
} > "$RESULTS_FILE"

BASELINE_TIME=0

for threads in "${THREADS_LIST[@]}"; do
    echo ">>> Running with $threads threads..." | tee -a "$RESULTS_FILE"
    
    OUTPUT=$(./wireroute -f "$INPUT" -n $threads -i $ITERATIONS -m A -b $BATCH 2>&1)
    
    COMP_TIME=$(echo "$OUTPUT" | grep "Computation time" | awk '{print $4}')
    
    if [ -z "$COMP_TIME" ]; then
        echo "  ERROR: Could not extract time" | tee -a "$RESULTS_FILE"
        continue
    fi
    
    if [ $threads -eq 1 ]; then
        BASELINE_TIME=$COMP_TIME
        SPEEDUP="1.00"
    else
        SPEEDUP=$(echo "scale=2; $BASELINE_TIME / $COMP_TIME" | bc)
    fi
    
    EFFICIENCY=$(echo "scale=1; 100 * $SPEEDUP / $threads" | bc)
    
    echo "  Threads: $threads | Time: ${COMP_TIME}s | Speedup: ${SPEEDUP}x | Efficiency: ${EFFICIENCY}%" | tee -a "$RESULTS_FILE"
    echo "" | tee -a "$RESULTS_FILE"
done

{
    echo "=========================================="
    echo ""
    echo "SUMMARY:"
    echo "  Baseline (1 thread): ${BASELINE_TIME}s"
    echo ""
    echo "Optimizations applied:"
    echo "  - CPU Governor: performance mode"
    echo "  - Thread Affinity: close binding to physical cores"
    echo "  - Compiler: -O3 -march=native -flto -ffast-math"
    echo ""
} | tee -a "$RESULTS_FILE"

echo "Results saved to: $RESULTS_FILE"
