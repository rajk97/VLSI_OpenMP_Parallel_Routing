#!/bin/bash

###############################################################################
# Benchmark Script for Within-Wire Parallelization Evaluation
# Runs tests on all input files with various thread counts
###############################################################################

echo "=========================================="
echo "Within-Wire Parallelization Benchmark"
echo "=========================================="
echo ""

# Log file
LOG_FILE="within_wire_benchmark.log"
RESULTS_FILE="within_wire_results.csv"

# CSV Header
echo "Input,Threads,ComputationTime,TotalTime,Cost,MaxOccupancy,Validation" > $RESULTS_FILE

# Test inputs
INPUTS=("easy_4096" "medium_4096" "hard_4096" "extreme_4096" "impossible_4096")

# Thread counts (adjust based on system)
THREADS=(1 2 4 8 16 32 64 128)

echo "Starting benchmarks..." | tee -a $LOG_FILE
echo "Inputs: ${INPUTS[@]}" | tee -a $LOG_FILE
echo "Thread counts: ${THREADS[@]}" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

for input in "${INPUTS[@]}"; do
    input_file="inputs/timeinput/${input}.txt"
    if [ ! -f "$input_file" ]; then
        echo "Warning: $input_file not found, skipping" | tee -a $LOG_FILE
        continue
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a $LOG_FILE
    echo "Testing: $input" | tee -a $LOG_FILE
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a $LOG_FILE

    for threads in "${THREADS[@]}"; do
        echo "" | tee -a $LOG_FILE
        echo "Running $input with $threads thread(s)..." | tee -a $LOG_FILE

        # Run the program and capture output
        OUTPUT=$( { time -p ./wireroute -f "$input_file" -n "$threads" -i 5 -m W; } 2>&1 )

        # Extract timing
        REAL_TIME=$(echo "$OUTPUT" | grep "^real" | awk '{print $2}')
        USER_TIME=$(echo "$OUTPUT" | grep "^user" | awk '{print $2}')
        SYS_TIME=$(echo "$OUTPUT" | grep "^sys" | awk '{print $2}')

        # Extract program metrics
        COMP_TIME=$(echo "$OUTPUT" | grep "Computation time" | awk '{print $4}')
        COST=$(echo "$OUTPUT" | grep "Total cost:" | awk '{print $3}')
        MAX_OCC=$(echo "$OUTPUT" | grep "Max occupancy:" | awk '{print $3}')

        echo "  Computation Time: ${COMP_TIME}s" | tee -a $LOG_FILE
        echo "  Total Time: ${REAL_TIME}s" | tee -a $LOG_FILE
        echo "  Cost: $COST" | tee -a $LOG_FILE
        echo "  Max Occupancy: $MAX_OCC" | tee -a $LOG_FILE

        # Validate output
        ROUTES_FILE="routes_${input}_${threads}.txt"
        OCCUPANCY_FILE="occupancy_${input}_${threads}.txt"

        VALIDATION="N/A"
        if [ -f "$ROUTES_FILE" ] && [ -f "$OCCUPANCY_FILE" ]; then
            VALIDATE_OUTPUT=$(python3 validate.py -r "$ROUTES_FILE" -c "$OCCUPANCY_FILE" 2>&1)
            if echo "$VALIDATE_OUTPUT" | grep -q "succeeded"; then
                VALIDATION="PASS"
                echo "  ✅ Validation: PASS" | tee -a $LOG_FILE
            else
                VALIDATION="FAIL"
                echo "  ❌ Validation: FAIL" | tee -a $LOG_FILE
            fi
        else
            echo "  ⚠️  Output files not found for validation" | tee -a $LOG_FILE
        fi

        # Save to CSV
        echo "$input,$threads,$COMP_TIME,$REAL_TIME,$COST,$MAX_OCC,$VALIDATION" >> $RESULTS_FILE

        # Save full output to log
        echo "----------------------------------------" >> $LOG_FILE
        echo "$OUTPUT" >> $LOG_FILE
        echo "----------------------------------------" >> $LOG_FILE
    done
done

echo "" | tee -a $LOG_FILE
echo "==========================================" | tee -a $LOG_FILE
echo "Benchmark Complete!" | tee -a $LOG_FILE
echo "Results saved to: $RESULTS_FILE" | tee -a $LOG_FILE
echo "Full log saved to: $LOG_FILE" | tee -a $LOG_FILE
echo "==========================================" | tee -a $LOG_FILE