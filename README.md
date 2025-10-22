# VLSI Wire Routing with OpenMP Parallelization

High-performance parallel wire routing implementation for VLSI circuit design using OpenMP. This project implements the **within-wire parallelization** approach, achieving up to **5.73x speedup** on 8 cores.

[![Language](https://img.shields.io/badge/language-C++17-blue.svg)](https://isocpp.org/)
[![OpenMP](https://img.shields.io/badge/OpenMP-4.0+-green.svg)](https://www.openmp.org/)
[![License](https://img.shields.io/badge/license-Academic-red.svg)](LICENSE)

## 📊 Performance Highlights

| Input Size | Wires | Sequential Time | Parallel Time (8 threads) | Speedup |
|------------|-------|-----------------|---------------------------|---------|
| Easy | 169 | 2.84s | 0.64s | **4.43x** |
| Medium | 595 | 35.17s | 6.14s | **5.73x** ⭐ |
| Hard | 1,123 | 46.90s | 9.28s | **5.05x** |

## 🎯 Project Overview

This implementation solves the VLSI wire routing problem using parallel simulated annealing. Given a grid and a set of wires (start/end points), the algorithm finds optimal routes that minimize congestion while satisfying routing constraints.

**Key Features:**
- ✅ Within-wire parallelization strategy
- ✅ Dynamic scheduling for load balancing
- ✅ Simulated annealing optimization
- ✅ Thread-safe critical sections
- ✅ Manhattan routing with max 2 bends
- ✅ Validated routing quality

## 🏗️ Repository Structure

```
.
├── code/                      # Source code and implementation
│   ├── wireroute.cpp         # Main routing algorithm with OpenMP
│   ├── wireroute.h           # Data structures (Wire, Route, Point)
│   ├── validate.cpp/py       # Validation utilities
│   ├── Makefile              # Build configuration
│   └── inputs/               # Test input files
│       ├── testinput/        # Small test cases
│       └── timeinput/        # Benchmark inputs
├── results/                   # Benchmark results and logs
│   ├── within_wire_final_benchmarks.csv
│   ├── BENCHMARK_SUMMARY.md
│   └── *.log files
├── docs/                      # Documentation
│   └── within_wire_performance_report.md
├── examples/                  # OpenMP example code
├── tutorials/                 # OpenMP tutorials and references
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites
- GCC 7.0+ with OpenMP support
- C++17 compatible compiler
- Make build system

### Building

```bash
cd code
make clean && make
```

### Running

```bash
# Basic usage
./wireroute -f <input_file> -n <num_threads> -m W -b 1

# Example: Run easy input with 8 threads
./wireroute -f inputs/timeinput/easy_4096.txt -n 8 -m W -b 1

# Options:
#   -f: Input file path
#   -n: Number of threads
#   -m: Parallelization mode (W = within-wire)
#   -b: Batch size (set to 1 for within-wire)
#   -p: SA probability (default: 0.1)
#   -i: SA iterations (default: 5)
```

### Validation

```bash
# Python validation
python3 validate.py -r routes_<input>_<threads>.txt -c occupancy_<input>_<threads>.txt

# C++ validation
./validate routes_<input>_<threads>.txt occupancy_<input>_<threads>.txt
```

## 🔬 Implementation Details

### Within-Wire Parallelization

The within-wire approach parallelizes candidate route evaluation for each individual wire:

```cpp
for each wire (sequential):
    #pragma omp parallel
    {
        #pragma omp for schedule(dynamic)
        for each candidate route (parallel):
            evaluate cost using occupancy grid
            track thread-local minimum
        
        #pragma omp critical
        update global best route
    }
    update occupancy grid (sequential)
```

**Algorithm Flow:**
1. **Phase 1**: Initial greedy placement
   - For each wire, enumerate 5-15 candidate routes
   - Evaluate costs in parallel with dynamic scheduling
   - Select best route and update occupancy

2. **Phase 2**: Simulated annealing (5 iterations)
   - Remove current wire from occupancy
   - Re-evaluate all candidates in parallel
   - Accept random route with probability 0.1
   - Update occupancy with selected route

### Key Optimizations

1. **Dynamic Scheduling**: Better load balancing for varying candidate complexities
2. **Thread-Local Reduction**: Each thread maintains private best route/cost
3. **Critical Sections**: Safe global updates without data races
4. **Occupancy Grid**: Efficient cost calculation using incremental updates

### Cost Function

Routes are evaluated using a sum-of-squares occupancy cost:
```
cost = Σ (2 * occupancy[point] + 1)
```
This encourages spreading wires across the grid to minimize congestion.

## 📈 Performance Analysis

See [`results/BENCHMARK_SUMMARY.md`](results/BENCHMARK_SUMMARY.md) for detailed performance analysis.

**Key Findings:**
- **Best speedup**: 5.73x on medium input (595 wires) with 8 threads
- **Scalability**: Better with larger inputs due to amortized thread overhead
- **Efficiency**: 71.6% efficiency maintained at 8 threads for medium input
- **Quality**: Consistent solution quality across thread counts

**Limitations:**
- Sequential outer loop (Amdahl's Law applies)
- Thread creation overhead (169-1123 parallel regions)
- Fine-grained parallelism (5-15 candidates per wire)

## 🔧 Development

### Compiler Flags
```makefile
CXXFLAGS = -Wall -O3 -std=c++17 -m64 -fopenmp
```

### Testing
```bash
# Run all benchmarks
cd code
for t in 1 2 4 8; do
    ./wireroute -f inputs/timeinput/easy_4096.txt -n $t -m W -b 1
done
```

## 📚 References

- Assignment based on CMU 15-418/618 (Parallel Computer Architecture and Programming)
- OpenMP 4.0+ specification
- VLSI routing algorithms and simulated annealing optimization

## 📝 License

Academic use only. Please review the course's policy on [academic integrity](http://www.cs.cmu.edu/~418/academicintegrity.html).





