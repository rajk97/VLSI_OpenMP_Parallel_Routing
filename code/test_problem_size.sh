#!/bin/bash

# ============================================================================
# Problem Size Sensitivity Study
# Tests different grid sizes and wire counts with 1 and 8 threads
# ============================================================================

OUTPUT_DIR="problem_size_results"
ITERATIONS=5
MODE="A"
BATCH_SIZE=1
P_VALUE=0.1  # Default SA probability

THREAD_COUNTS=(1 8)

echo "Problem Size Sensitivity Study"
echo "=============================="
echo "Date: $(date)"
echo "Iterations: $ITERATIONS"
echo "Mode: $MODE (Across-wires)"
echo "Batch size: $BATCH_SIZE"
echo "P value: $P_VALUE"
echo ""

# Create output directory
mkdir -p $OUTPUT_DIR

# Test Grid Size Sensitivity
echo "========================================"
echo "PART 1: Grid Size Sensitivity"
echo "========================================"
echo ""

GRIDSIZE_FILES=(
    "inputs/problemsize/gridsize/hard_2048.txt"
    "inputs/problemsize/gridsize/hard_4096.txt"
    "inputs/problemsize/gridsize/hard_8192.txt"
)

for input_file in "${GRIDSIZE_FILES[@]}"; do
    # Extract grid size from filename
    filename=$(basename $input_file)
    grid_size=$(echo $filename | grep -oP '\d+' | head -1)
    
    for threads in "${THREAD_COUNTS[@]}"; do
        echo "----------------------------------------"
        echo "Testing: $filename (${grid_size}x${grid_size})"
        echo "Threads: $threads"
        echo "----------------------------------------"
        
        LOG_FILE="$OUTPUT_DIR/gridsize_${grid_size}_threads_${threads}.log"
        
        # Run wireroute
        ./wireroute -f $input_file -n $threads -i $ITERATIONS -m $MODE -b $BATCH_SIZE -p $P_VALUE \
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

# Test Wire Count Sensitivity
echo ""
echo "========================================"
echo "PART 2: Wire Count Sensitivity"
echo "========================================"
echo ""

NUMWIRES_FILES=(
    "inputs/problemsize/numwires/hard_4096_539.txt"
    "inputs/problemsize/numwires/hard_4096_1123.txt"
    "inputs/problemsize/numwires/hard_4096_1581.txt"
)

for input_file in "${NUMWIRES_FILES[@]}"; do
    # Extract wire count from filename
    filename=$(basename $input_file)
    wire_count=$(echo $filename | grep -oP '\d+' | tail -1)
    
    for threads in "${THREAD_COUNTS[@]}"; do
        echo "----------------------------------------"
        echo "Testing: $filename ($wire_count wires, 4096x4096 grid)"
        echo "Threads: $threads"
        echo "----------------------------------------"
        
        LOG_FILE="$OUTPUT_DIR/numwires_${wire_count}_threads_${threads}.log"
        
        # Run wireroute
        ./wireroute -f $input_file -n $threads -i $ITERATIONS -m $MODE -b $BATCH_SIZE -p $P_VALUE \
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
echo "Problem Size Sensitivity Study Summary" > $SUMMARY_FILE
echo "======================================" >> $SUMMARY_FILE
echo "Date: $(date)" >> $SUMMARY_FILE
echo "" >> $SUMMARY_FILE

echo "PART 1: Grid Size Sensitivity" >> $SUMMARY_FILE
echo "------------------------------" >> $SUMMARY_FILE
printf "%-10s %-10s %-15s %-15s %-15s\n" "Grid Size" "Threads" "Comp Time (s)" "Total Cost" "Max Occ" >> $SUMMARY_FILE
echo "------------------------------------------------------------------------" >> $SUMMARY_FILE

for input_file in "${GRIDSIZE_FILES[@]}"; do
    filename=$(basename $input_file)
    grid_size=$(echo $filename | grep -oP '\d+' | head -1)
    
    for threads in "${THREAD_COUNTS[@]}"; do
        LOG_FILE="$OUTPUT_DIR/gridsize_${grid_size}_threads_${threads}.log"
        comp_time=$(grep "Computation time (sec):" $LOG_FILE | awk '{print $4}')
        total_cost=$(grep "Total cost:" $LOG_FILE | awk '{print $3}')
        max_occ=$(grep "Max occupancy:" $LOG_FILE | awk '{print $3}')
        
        printf "%-10s %-10s %-15s %-15s %-15s\n" "${grid_size}x${grid_size}" "$threads" "$comp_time" "$total_cost" "$max_occ" >> $SUMMARY_FILE
    done
done

echo "" >> $SUMMARY_FILE
echo "Speedup Analysis (Grid Size):" >> $SUMMARY_FILE
echo "----------------------------" >> $SUMMARY_FILE

for input_file in "${GRIDSIZE_FILES[@]}"; do
    filename=$(basename $input_file)
    grid_size=$(echo $filename | grep -oP '\d+' | head -1)
    
    LOG_1T="$OUTPUT_DIR/gridsize_${grid_size}_threads_1.log"
    LOG_8T="$OUTPUT_DIR/gridsize_${grid_size}_threads_8.log"
    
    time_1t=$(grep "Computation time (sec):" $LOG_1T | awk '{print $4}')
    time_8t=$(grep "Computation time (sec):" $LOG_8T | awk '{print $4}')
    
    speedup=$(echo "scale=2; $time_1t / $time_8t" | bc)
    
    echo "${grid_size}x${grid_size}: Speedup = $speedup x ($time_1t s / $time_8t s)" >> $SUMMARY_FILE
done

echo "" >> $SUMMARY_FILE
echo "PART 2: Wire Count Sensitivity" >> $SUMMARY_FILE
echo "------------------------------" >> $SUMMARY_FILE
printf "%-12s %-10s %-15s %-15s %-15s\n" "Wire Count" "Threads" "Comp Time (s)" "Total Cost" "Max Occ" >> $SUMMARY_FILE
echo "------------------------------------------------------------------------" >> $SUMMARY_FILE

for input_file in "${NUMWIRES_FILES[@]}"; do
    filename=$(basename $input_file)
    wire_count=$(echo $filename | grep -oP '\d+' | tail -1)
    
    for threads in "${THREAD_COUNTS[@]}"; do
        LOG_FILE="$OUTPUT_DIR/numwires_${wire_count}_threads_${threads}.log"
        comp_time=$(grep "Computation time (sec):" $LOG_FILE | awk '{print $4}')
        total_cost=$(grep "Total cost:" $LOG_FILE | awk '{print $3}')
        max_occ=$(grep "Max occupancy:" $LOG_FILE | awk '{print $3}')
        
        printf "%-12s %-10s %-15s %-15s %-15s\n" "$wire_count" "$threads" "$comp_time" "$total_cost" "$max_occ" >> $SUMMARY_FILE
    done
done

echo "" >> $SUMMARY_FILE
echo "Speedup Analysis (Wire Count):" >> $SUMMARY_FILE
echo "-----------------------------" >> $SUMMARY_FILE

for input_file in "${NUMWIRES_FILES[@]}"; do
    filename=$(basename $input_file)
    wire_count=$(echo $filename | grep -oP '\d+' | tail -1)
    
    LOG_1T="$OUTPUT_DIR/numwires_${wire_count}_threads_1.log"
    LOG_8T="$OUTPUT_DIR/numwires_${wire_count}_threads_8.log"
    
    time_1t=$(grep "Computation time (sec):" $LOG_1T | awk '{print $4}')
    time_8t=$(grep "Computation time (sec):" $LOG_8T | awk '{print $4}')
    
    speedup=$(echo "scale=2; $time_1t / $time_8t" | bc)
    
    echo "$wire_count wires: Speedup = $speedup x ($time_1t s / $time_8t s)" >> $SUMMARY_FILE
done

cat $SUMMARY_FILE

echo ""
echo "Next step: Run 'python3 plot_problem_size.py' to generate graphs"
