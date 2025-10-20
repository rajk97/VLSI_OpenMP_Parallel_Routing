#!/bin/bash

# Tracy Profile Collection Script
# Generates .tracy files for different configurations for performance analysis

TRACY_CAPTURE="/home/raj/Documents/Projects/system_software/tracy/capture/build/tracy-capture"
WIREROUTE="./wireroute"
TRACY_DIR="tracy_profiles"

# Create directory for Tracy profiles
mkdir -p "$TRACY_DIR"

# Configuration arrays
# Note: Adjust thread counts based on your machine (e.g., remove 16,32,64,128 if not on PSC)
INPUTS=("easy_4096.txt" "medium_4096.txt" "hard_4096.txt")
THREADS=(1 2 4 8)
SA_ITERATIONS=5
BATCH_SIZE=1

echo "=== Tracy Profile Collection ==="
echo "Tracy capture tool: $TRACY_CAPTURE"
echo "Wireroute binary: $WIREROUTE"
echo "Output directory: $TRACY_DIR"
echo ""

# Check if Tracy-enabled build exists
if [ ! -f "$WIREROUTE" ]; then
    echo "ERROR: wireroute binary not found. Build with 'make TRACY_ENABLED=1' first."
    exit 1
fi

# Check if it's Tracy-enabled (approximate check by file size)
FILESIZE=$(stat -f%z "$WIREROUTE" 2>/dev/null || stat -c%s "$WIREROUTE" 2>/dev/null)
if [ "$FILESIZE" -lt 200000 ]; then
    echo "WARNING: wireroute binary seems small ($FILESIZE bytes). Did you build with TRACY_ENABLED=1?"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Starting profile collection..."
echo ""

# Collect profiles for each configuration
for input in "${INPUTS[@]}"; do
    INPUT_FILE="inputs/timeinput/$input"
    INPUT_NAME="${input%.txt}"
    
    if [ ! -f "$INPUT_FILE" ]; then
        echo "WARNING: Input file $INPUT_FILE not found. Skipping."
        continue
    fi
    
    for threads in "${THREADS[@]}"; do
        PROFILE_NAME="${INPUT_NAME}_t${threads}"
        TRACE_FILE="${TRACY_DIR}/${PROFILE_NAME}.tracy"
        
        echo "----------------------------------------"
        echo "Configuration: $input with $threads threads"
        echo "Output: $TRACE_FILE"
        
        # Start Tracy capture in background
        ($TRACY_CAPTURE -o "$TRACE_FILE" -f > /dev/null 2>&1 &)
        CAPTURE_PID=$!
        
        # Wait for Tracy capture to initialize
        sleep 3
        
        # Run wireroute with Tracy instrumentation
        echo "Running wireroute..."
        $WIREROUTE -f "$INPUT_FILE" -n $threads -i $SA_ITERATIONS -m A -b $BATCH_SIZE
        
        # Wait for Tracy to capture the session
        sleep 2
        
        # Tracy capture should auto-terminate, but kill if needed
        kill $CAPTURE_PID 2>/dev/null
        wait $CAPTURE_PID 2>/dev/null
        
        # Check if trace was generated
        if [ -f "$TRACE_FILE" ]; then
            TRACE_SIZE=$(stat -f%z "$TRACE_FILE" 2>/dev/null || stat -c%s "$TRACE_FILE" 2>/dev/null)
            echo "✓ Trace collected: $TRACE_FILE ($(numfmt --to=iec-i --suffix=B $TRACE_SIZE 2>/dev/null || echo "$TRACE_SIZE bytes"))"
        else
            echo "✗ Failed to generate trace file"
        fi
        
        echo ""
    done
done

echo "========================================"
echo "Profile collection complete!"
echo ""
echo "Generated profiles:"
ls -lh "$TRACY_DIR"/*.tracy 2>/dev/null || echo "No traces found"
echo ""
echo "Next steps:"
echo "1. Upload traces to https://tracy.nereid.pl/"
echo "2. Analyze thread timelines, load balance, and zone times"
echo "3. Compare profiles across thread counts to identify bottlenecks"
echo "4. Look for: synchronization overhead, load imbalance, idle time"
