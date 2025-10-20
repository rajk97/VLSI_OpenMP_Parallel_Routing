#!/bin/bash
# Script to collect cache miss data for different thread counts
# Usage: ./collect_cache_misses.sh

OUTPUT_FILE="cache_misses_data.txt"
INPUT_FILE="inputs/timeinput/medium_4096.txt"
MODE="A"
BATCH_SIZE="1"
ITERATIONS="5"

echo "Cache Miss Data Collection" > $OUTPUT_FILE
echo "==========================" >> $OUTPUT_FILE
echo "Date: $(date)" >> $OUTPUT_FILE
echo "Input: $INPUT_FILE" >> $OUTPUT_FILE
echo "Mode: $MODE (across-wire)" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

for threads in 1 2 4 8; do
    echo "Collecting data for $threads threads..."
    echo "" >> $OUTPUT_FILE
    echo ">>> Threads: $threads" >> $OUTPUT_FILE
    echo "----------------------------" >> $OUTPUT_FILE
    
    # Run perf stat to collect cache miss data
    # -e cache-misses: count cache misses
    # -e cache-references: count total cache accesses
    # -e LLC-load-misses: count Last Level Cache (L3) load misses
    # -e LLC-loads: count L3 cache loads
    perf stat -e cache-misses,cache-references,LLC-load-misses,LLC-loads \
        ./wireroute -f $INPUT_FILE -n $threads -i $ITERATIONS -m $MODE -b $BATCH_SIZE \
        2>&1 | tee -a $OUTPUT_FILE
    
    echo "" >> $OUTPUT_FILE
    echo "========================================" >> $OUTPUT_FILE
    echo "" >> $OUTPUT_FILE
done

echo ""
echo "Data collection complete!"
echo "Results saved to: $OUTPUT_FILE"
echo ""
echo "Next step: Run 'python3 plot_cache_misses.py' to generate graphs"
