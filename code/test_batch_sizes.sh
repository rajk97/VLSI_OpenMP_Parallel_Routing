#!/bin/bash
# Batch Size Sensitivity Study
# Tests different batch sizes to explore performance vs quality tradeoff

OUTPUT_DIR="batch_sensitivity_results"
INPUT_FILE="inputs/timeinput/medium_4096.txt"
THREADS=8
ITERATIONS=5
MODE="A"

# Create output directory
mkdir -p $OUTPUT_DIR

echo "Batch Size Sensitivity Study" | tee $OUTPUT_DIR/summary.txt
echo "============================" | tee -a $OUTPUT_DIR/summary.txt
echo "Date: $(date)" | tee -a $OUTPUT_DIR/summary.txt
echo "Input: $INPUT_FILE" | tee -a $OUTPUT_DIR/summary.txt
echo "Threads: $THREADS" | tee -a $OUTPUT_DIR/summary.txt
echo "Iterations: $ITERATIONS" | tee -a $OUTPUT_DIR/summary.txt
echo "" | tee -a $OUTPUT_DIR/summary.txt

# Test different batch sizes
BATCH_SIZES=(1 5 10 25 50 100)

echo "Batch Sizes to test: ${BATCH_SIZES[@]}" | tee -a $OUTPUT_DIR/summary.txt
echo "" | tee -a $OUTPUT_DIR/summary.txt

for batch in "${BATCH_SIZES[@]}"; do
    echo "========================================" | tee -a $OUTPUT_DIR/summary.txt
    echo "Testing batch_size = $batch" | tee -a $OUTPUT_DIR/summary.txt
    echo "========================================" | tee -a $OUTPUT_DIR/summary.txt
    
    # Run the program
    ./wireroute -f $INPUT_FILE -n $THREADS -i $ITERATIONS -m $MODE -b $batch \
        2>&1 | tee $OUTPUT_DIR/batch_${batch}.log
    
    # Extract key metrics
    comp_time=$(grep "Computation time" $OUTPUT_DIR/batch_${batch}.log | awk '{print $4}')
    total_cost=$(grep "Total cost:" $OUTPUT_DIR/batch_${batch}.log | awk '{print $3}')
    max_occupancy=$(grep "Max occupancy:" $OUTPUT_DIR/batch_${batch}.log | awk '{print $3}')
    
    echo "  Computation time: $comp_time s" | tee -a $OUTPUT_DIR/summary.txt
    echo "  Total cost: $total_cost" | tee -a $OUTPUT_DIR/summary.txt
    echo "  Max occupancy: $max_occupancy" | tee -a $OUTPUT_DIR/summary.txt
    echo "" | tee -a $OUTPUT_DIR/summary.txt
done

echo "========================================" | tee -a $OUTPUT_DIR/summary.txt
echo "Data collection complete!" | tee -a $OUTPUT_DIR/summary.txt
echo "Results saved to: $OUTPUT_DIR/" | tee -a $OUTPUT_DIR/summary.txt
echo "" | tee -a $OUTPUT_DIR/summary.txt
echo "Next step: Run 'python3 plot_batch_sensitivity.py' to generate graphs" | tee -a $OUTPUT_DIR/summary.txt
