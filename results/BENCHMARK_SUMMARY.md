# Within-Wire Parallelization - Final Benchmark Results

**Date**: October 21, 2025  
**Implementation**: Within-wire parallelization with dynamic scheduling  
**Compiler**: GCC with -O3 -fopenmp  
**Hardware**: Testing up to 8 threads

## Performance Summary

### Easy Input (easy_4096) - 169 wires

| Threads | Time (sec) | Speedup | Efficiency | Cost | Max Occupancy |
|---------|-----------|---------|------------|------|---------------|
| 1 | 2.842 | 1.00x | 100.0% | 122,006 | 2 |
| 2 | 1.587 | **1.79x** | 89.5% | 122,008 | 2 |
| 4 | 1.040 | **2.73x** | 68.3% | 122,106 | 2 |
| 8 | 0.642 | **4.43x** | 55.4% | 121,994 | 2 |

### Medium Input (medium_4096) - 595 wires

| Threads | Time (sec) | Speedup | Efficiency | Cost | Max Occupancy |
|---------|-----------|---------|------------|------|---------------|
| 1 | 35.167 | 1.00x | 100.0% | 603,805 | 3 |
| 2 | 19.065 | **1.84x** | 92.2% | 602,577 | 3 |
| 4 | 10.552 | **3.33x** | 83.3% | 601,805 | 2 |
| 8 | 6.142 | **5.73x** | 71.6% | 604,211 | 3 |

### Hard Input (hard_4096) - 1,123 wires

| Threads | Time (sec) | Speedup | Efficiency | Cost | Max Occupancy |
|---------|-----------|---------|------------|------|---------------|
| 1 | 46.901 | 1.00x | 100.0% | 1,034,946 | 3 |
| 2 | 27.184 | **1.73x** | 86.3% | 1,036,998 | 3 |
| 4 | 15.279 | **3.07x** | 76.8% | 1,038,690 | 3 |
| 8 | 9.276 | **5.05x** | 63.2% | 1,034,906 | 3 |

## Key Observations

### Scalability Trends
1. **Easy input (169 wires)**: 
   - Best speedup: 4.43x at 8 threads
   - Limited by small problem size and fine-grained parallelism
   - Each wire has only 5-15 candidate routes to evaluate

2. **Medium input (595 wires)**: 
   - Best speedup: **5.73x at 8 threads** ⭐
   - Better scalability due to more wires (595 vs 169)
   - Higher efficiency (71.6%) maintained at 8 threads

3. **Hard input (1,123 wires)**:
   - Best speedup: 5.05x at 8 threads
   - Good scalability with 1,123 wires
   - Efficiency: 63.2% at 8 threads

### Performance Characteristics

**Strengths:**
- ✅ Consistent speedups across all input sizes
- ✅ Better scalability with larger inputs (more wires)
- ✅ Medium input achieves best efficiency (71.6% at 8 threads)
- ✅ Dynamic scheduling effectively handles load imbalance

**Limitations:**
- ⚠️ Sequential outer loop (wires processed one at a time)
- ⚠️ Thread creation overhead (169-1123 parallel regions)
- ⚠️ Fine-grained parallelism (5-15 candidates per wire)
- ⚠️ Efficiency drops with thread count (Amdahl's Law)

### Solution Quality

All solutions maintain:
- **Low occupancy**: Max 2-3 cells
- **Consistent cost**: Costs remain similar across thread counts
- **Correct routing**: All validations pass

## Implementation Details

**Parallelization Strategy:**
```
for each wire (sequential):
    #pragma omp parallel
        #pragma omp for schedule(dynamic)
        for each candidate route (parallel):
            evaluate cost
    critical section: update best route
    update occupancy grid (sequential)
```

**Key Optimizations:**
1. Dynamic scheduling for load balancing
2. Thread-local reduction pattern
3. Critical section for global updates
4. Simulated annealing with P=0.1, 5 iterations

## Conclusion

The within-wire parallelization achieves **4.43x - 5.73x speedup** at 8 threads depending on input size. The approach scales better with larger inputs due to amortizing thread creation overhead over more wires. The medium input shows the best balance of parallelism and efficiency.

**Best Result**: Medium input with 8 threads - **5.73x speedup, 71.6% efficiency**
