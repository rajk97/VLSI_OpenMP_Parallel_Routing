#!/bin/bash

# ============================================================================
# SA Probability Sensitivity Study
# Tests P values: 0.01, 0.1, 0.5 with 1 and 8 threads
# ============================================================================

OUTPUT_DIR="sa_probability_results"
INPUT_FILE="inputs/timeinput/medium_4096.txt"
ITERATIONS=5
MODE="A"
BATCH_SIZE=1

# SA probabilities to test
P_VALUES=(0.01 0.1 0.5)
THREAD_COUNTS=(1 8)

echo "SA Probability Sensitivity Study"
echo "=================================="
echo "Date: $(date)"
echo "Input: $INPUT_FILE"
echo "Iterations: $ITERATIONS"
echo "Mode: $MODE (Across-wires)"
echo "Batch size: $BATCH_SIZE"
echo ""
echo "P values to test: ${P_VALUES[@]}"
echo "Thread counts: ${THREAD_COUNTS[@]}"
echo ""

# Create output directory
mkdir -p $OUTPUT_DIR

# Run experiments
for p in "${P_VALUES[@]}"; do
    for threads in "${THREAD_COUNTS[@]}"; do
        echo "========================================"
        echo "Testing P=$p with $threads thread(s)"
        echo "========================================"
        
        LOG_FILE="$OUTPUT_DIR/p_${p}_threads_${threads}.log"
        
        # Run wireroute
        ./wireroute -f $INPUT_FILE -n $threads -i $ITERATIONS -m $MODE -b $BATCH_SIZE -p $p \
            2>&1 | tee $LOG_FILE
        
        # Extract key metrics
        comp_time=$(grep "Computation time (sec):" $LOG_FILE | awk '{print $4}')
        total_cost=$(grep "Total cost:" $LOG_FILE | awk '{print $3}')
        max_occ=$(grep "Max occupancy:" $LOG_FILE | awk '{print $3}')
        
        echo "  Computation time: $comp_time s"
        echo "  Total cost: $total_cost"
        echo "  Max occupancy: $max_occ"
        echo ""
    done
done

echo "========================================"
echo "Data collection complete!"
echo "Results saved to: $OUTPUT_DIR/"
echo ""
echo "Generating summary..."
echo "========================================"

# Generate summary file
SUMMARY_FILE="$OUTPUT_DIR/summary.txt"
echo "SA Probability Sensitivity Study Summary" > $SUMMARY_FILE
echo "========================================" >> $SUMMARY_FILE
echo "Date: $(date)" >> $SUMMARY_FILE
echo "" >> $SUMMARY_FILE
printf "%-8s %-10s %-15s %-15s %-15s\n" "P Value" "Threads" "Comp Time (s)" "Total Cost" "Max Occ" >> $SUMMARY_FILE
echo "------------------------------------------------------------------------" >> $SUMMARY_FILE

for p in "${P_VALUES[@]}"; do
    for threads in "${THREAD_COUNTS[@]}"; do
        LOG_FILE="$OUTPUT_DIR/p_${p}_threads_${threads}.log"
        comp_time=$(grep "Computation time (sec):" $LOG_FILE | awk '{print $4}')
        total_cost=$(grep "Total cost:" $LOG_FILE | awk '{print $3}')
        max_occ=$(grep "Max occupancy:" $LOG_FILE | awk '{print $3}')
        
        printf "%-8s %-10s %-15s %-15s %-15s\n" "$p" "$threads" "$comp_time" "$total_cost" "$max_occ" >> $SUMMARY_FILE
    done
done

echo "" >> $SUMMARY_FILE
echo "Speedup Analysis:" >> $SUMMARY_FILE
echo "----------------" >> $SUMMARY_FILE

for p in "${P_VALUES[@]}"; do
    LOG_1T="$OUTPUT_DIR/p_${p}_threads_1.log"
    LOG_8T="$OUTPUT_DIR/p_${p}_threads_8.log"
    
    time_1t=$(grep "Computation time (sec):" $LOG_1T | awk '{print $4}')
    time_8t=$(grep "Computation time (sec):" $LOG_8T | awk '{print $4}')
    
    speedup=$(echo "scale=2; $time_1t / $time_8t" | bc)
    
    echo "P=$p: Speedup = $speedup x ($time_1t s / $time_8t s)" >> $SUMMARY_FILE
done

cat $SUMMARY_FILE

echo ""
echo "Next step: Run 'python3 plot_sa_probability.py' to generate graphs"
