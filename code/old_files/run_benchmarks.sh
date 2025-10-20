#!/bin/bash

mkdir -p logs

# Run benchmarks for each file and thread count
for file in easy_4096.txt medium_4096.txt hard_4096.txt extreme_4096.txt impossible_4096.txt; do
    for threads in 1 2 4 8 16 32 64 128; do
        echo "Running $file with $threads threads..."
        ./wireroute -f inputs/timeinput/$file -n $threads -i 5 -m A -b 1 > logs/${file}_${threads}.log 2>&1
        echo "Completed $file with $threads threads"
    done
done

echo "All benchmarks completed. Results saved in logs/ directory."
