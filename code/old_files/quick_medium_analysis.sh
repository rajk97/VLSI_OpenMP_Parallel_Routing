#!/bin/bash

# Quick Medium Input Analysis - Speedup + Tracy Profiles
# Focus: medium_4096.txt only, threads: 1, 2, 4, 8

TRACY_CAPTURE="/home/raj/Documents/Projects/system_software/tracy/capture/build/tracy-capture"
INPUT="inputs/timeinput/medium_4096.txt"
THREADS_LIST=(1 2 4 8)
ITERATIONS=5
BATCH=1

# Directories
PROFILE_DIR="medium_profiles"
mkdir -p "$PROFILE_DIR"

echo "=== Quick Medium Analysis ==="
echo "Input: $INPUT"
echo "Threads: ${THREADS_LIST[@]}"
echo ""

# Results file
RESULTS="medium_speedup_results.txt"
echo "Medium 4096 Speedup Analysis - $(date)" > "$RESULTS"
echo "==========================================" >> "$RESULTS"
echo "" >> "$RESULTS"

# Baseline time (will be set after first run)
BASELINE_TIME=0

for threads in "${THREADS_LIST[@]}"; do
    echo ">>> Running with $threads threads..."
    
    TRACE_FILE="${PROFILE_DIR}/medium_t${threads}.tracy"
    
    # Start Tracy capture
    ($TRACY_CAPTURE -o "$TRACE_FILE" -f > /dev/null 2>&1 &)
    CAPTURE_PID=$!
    sleep 3
    
    # Run and capture output
    OUTPUT=$(./wireroute -f "$INPUT" -n $threads -i $ITERATIONS -m A -b $BATCH 2>&1)
    
    sleep 2
    kill $CAPTURE_PID 2>/dev/null
    wait $CAPTURE_PID 2>/dev/null
    
    # Extract computation time (note: lowercase 'time')
    COMP_TIME=$(echo "$OUTPUT" | grep "Computation time" | awk '{print $4}')
    
    if [ -z "$COMP_TIME" ]; then
        echo "ERROR: Could not extract time for $threads threads"
        continue
    fi
    
    # Calculate speedup
    if [ $threads -eq 1 ]; then
        BASELINE_TIME=$COMP_TIME
        SPEEDUP="1.00"
    else
        SPEEDUP=$(echo "scale=2; $BASELINE_TIME / $COMP_TIME" | bc)
    fi
    
    # Print and save results
    echo "  Threads: $threads | Time: ${COMP_TIME}s | Speedup: ${SPEEDUP}x"
    echo "Threads: $threads | Time: ${COMP_TIME}s | Speedup: ${SPEEDUP}x" >> "$RESULTS"
    
    # Check trace file
    if [ -f "$TRACE_FILE" ]; then
        TRACE_SIZE=$(stat -c%s "$TRACE_FILE" 2>/dev/null)
        echo "  Tracy profile: $TRACE_FILE ($(numfmt --to=iec-i --suffix=B $TRACE_SIZE 2>/dev/null))"
    fi
    
    echo ""
done

echo "" >> "$RESULTS"
echo "Baseline (1 thread): ${BASELINE_TIME}s" >> "$RESULTS"
echo "" >> "$RESULTS"
echo "Tracy profiles saved in: $PROFILE_DIR/" >> "$RESULTS"

echo "==========================================="
echo "✓ Complete!"
echo ""
echo "Results saved to: $RESULTS"
echo "Tracy profiles in: $PROFILE_DIR/"
echo ""
echo "Next: Upload .tracy files to https://tracy.nereid.pl/ for comparison"
