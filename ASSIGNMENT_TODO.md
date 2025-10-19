# Assignment 3 - OpenMP Wire Routing TODO List

**Course:** CMU 15-418/618 Fall 2024  
**Student:** Raj  
**Current Status:** Across-wire implementation complete, optimization phase in progress  
**Last Updated:** October 18, 2025

---

## 📋 Implementation Checklist

### ✅ **COMPLETED**

- [x] **Basic Setup**
  - [x] Clone starter code
  - [x] Understand problem specification
  - [x] Set up development environment (GHC machines)
  
- [x] **Sequential Implementation**
  - [x] Read input files (format from Figure 1)
  - [x] Implement route enumeration (∆x + ∆y routes)
  - [x] Implement cost calculation (sum of squares)
  - [x] Implement initial greedy placement
  - [x] Implement simulated annealing iterations

- [x] **Across-Wire Parallelization (-m A)**
  - [x] Implement batch processing (batch size parameter -b)
  - [x] Implement parallel wire routing with OpenMP
  - [x] Add synchronization for occupancy matrix updates
  - [x] Implement 3-phase approach (remove, route, update)
  - [x] Add command-line argument parsing (-f, -n, -p, -i, -m, -b)

- [x] **Performance Optimization**
  - [x] Apply compiler optimizations (-O3, -march=native, -flto, -ffast-math)
  - [x] Enable CPU performance governor
  - [x] Configure thread affinity (OMP_PROC_BIND=close, OMP_PLACES=cores)
  - [x] Integrate Tracy profiler for performance analysis
  - [x] Optimize calculateRouteCost (inlined, simplified math)
  - [x] Achieve ~32% overall performance improvement

- [x] **Initial Benchmarking**
  - [x] Collect baseline performance data (1,2,4,8 threads)
  - [x] Generate Tracy profiles for medium input
  - [x] Measure speedup and efficiency

---

## 🚧 **IN PROGRESS**

### **Phase 1: Complete Implementation Requirements**

- [ ] **Within-Wire Parallelization (-m W)** [Priority: HIGH]
  - [ ] Design within-wire parallel strategy
  - [ ] Implement parallel route exploration for single wire
  - [ ] Add switch between -m W and -m A modes
  - [ ] Test correctness with test inputs
  - [ ] Benchmark performance (1,2,4,8 threads)
  - [ ] Generate Tracy profiles for within-wire mode
  - [ ] **Estimated time:** 4-6 hours

---

## 📊 **Phase 2: Performance Analysis & Writeup (GHC Machines)**

### **2.1 Within-Wires Approach Analysis** [Priority: HIGH - 20 points]

- [ ] **Design Journey Documentation**
  - [ ] Document initial design approach
  - [ ] Explain parallelization strategy (how routes are divided)
  - [ ] Describe synchronization approach (if any needed)
  - [ ] Discuss reasoning for implementation choices

- [ ] **Performance Debugging**
  - [ ] Run Tracy profiler on within-wire implementation
  - [ ] Identify bottlenecks (synchronization? load balance?)
  - [ ] Document optimization iterations
  - [ ] Explain why perfect speedup isn't achieved

- [ ] **Experimental Data Collection (1,2,4,8,16 threads)**
  - [ ] Total speedup graph
  - [ ] Computation speedup graph
  - [ ] Total cache misses vs threads
  - [ ] Per-thread cache misses vs threads
  - [ ] Analysis of cache miss trends

### **2.2 Across-Wires Approach Analysis** [Priority: HIGH - 40 points]

- [ ] **Design Journey Documentation**
  - [ ] Document evolution of approach (initial → final design)
  - [ ] Explain batch processing strategy and reasoning
  - [ ] Describe synchronization strategy (critical sections, atomics)
  - [ ] Discuss task assignment approach (dynamic work stealing)
  - [ ] Explain decisions about granularity of locking

- [ ] **Performance Debugging**
  - [ ] Analyze Tracy profiles (already collected)
  - [ ] Upload .tracy files to https://tracy.nereid.pl/
  - [ ] Take screenshots of timeline view, statistics view
  - [ ] Identify bottlenecks:
    - [ ] Synchronization overhead (critical sections)
    - [ ] Cache coherence traffic (atomic operations)
    - [ ] Load imbalance (thread utilization)
  - [ ] Document optimization iterations (calculateRouteCost already done!)
  - [ ] Explain efficiency drop at high thread counts

- [ ] **Experimental Data Collection (1,2,4,8,16 threads)**
  - [ ] Total speedup graph
  - [ ] Computation speedup graph
  - [ ] Total cache misses vs threads
  - [ ] Per-thread cache misses vs threads
  - [ ] Analysis of cache miss trends vs speedup

- [ ] **Compare Within-Wires vs Across-Wires**
  - [ ] Which approach scales better? Why?
  - [ ] Synchronization overhead comparison
  - [ ] Cache behavior comparison

### **2.3 Routing Output** [Priority: MEDIUM - 2 points]

- [ ] **Generate Visual Output**
  - [ ] Run both modes on medium_4096.txt with 8 threads
  - [ ] Use WireGrapher.java to visualize:
    - [ ] Within-wire routing output
    - [ ] Across-wire routing output
  - [ ] Take screenshots or export images
  - [ ] Report max occupancy and total cost for both

### **2.4 Sensitivity Studies (GHC)** [Priority: MEDIUM - 8 points]

- [ ] **Sensitivity to SA Probability (P)**
  - [ ] Test across-wire with P = 0.01, 0.1, 0.5
  - [ ] Measure computation speedup (8 threads vs 1 thread)
  - [ ] Create speedup graph vs P
  - [ ] Analyze impact on performance and quality
  - [ ] Discuss tradeoffs (exploration vs exploitation)

- [ ] **Sensitivity to Problem Size**
  - [ ] Run on inputs from `/code/inputs/problemsize/gridsize/`
    - [ ] hard_2048.txt
    - [ ] hard_4096.txt
    - [ ] hard_8192.txt
  - [ ] Run on inputs from `/code/inputs/problemsize/numwires/`
    - [ ] hard_4096_539.txt
    - [ ] hard_4096_1123.txt
    - [ ] hard_4096_1581.txt
  - [ ] Measure computation speedup (8 threads vs 1 thread)
  - [ ] Create speedup graphs:
    - [ ] Speedup vs grid size
    - [ ] Speedup vs number of wires
  - [ ] Discuss how problem characteristics affect parallelism

---

## 🖥️ **Phase 3: PSC Bridges-2 Experiments** [Priority: MEDIUM - 10 points]

**⚠️ IMPORTANT CONSTRAINTS:**
- Debug on GHC first - PSC time is limited!
- Maximum 10 experiments per day on PSC
- Only test stable, debugged code on PSC

### **3.1 PSC Setup**
- [ ] Review PSC tutorial: https://www.psc.edu/resources/bridges-2/user-guide/
- [ ] Transfer working code to PSC
- [ ] Verify code compiles and runs correctly
- [ ] Submit test job to verify SLURM configuration

### **3.2 Within-Wires on PSC**
- [ ] Run experiments with 16, 32, 64, 128 threads
- [ ] Collect total speedup data
- [ ] Collect computation speedup data
- [ ] Create speedup graphs

### **3.3 Across-Wires on PSC**
- [ ] Run experiments with 16, 32, 64, 128 threads
- [ ] Collect total speedup data
- [ ] Collect computation speedup data
- [ ] Create speedup graphs

### **3.4 PSC Analysis**
- [ ] Compare PSC vs GHC speedup curves
- [ ] Discuss scalability to higher thread counts
- [ ] Explain any performance differences:
  - [ ] NUMA effects (multi-socket system)
  - [ ] Cache hierarchy differences
  - [ ] Memory bandwidth bottlenecks
- [ ] Analyze efficiency at high thread counts (64, 128)

---

## 📝 **Phase 4: Final Writeup Assembly**

### **4.1 Report Structure**

**1. Within-Wires Design & Performance (20 points)**
- [ ] Design approach and evolution
- [ ] Implementation choices and reasoning
- [ ] Synchronization strategy
- [ ] Performance debugging journey
- [ ] Speedup graphs (GHC: 1,2,4,8,16 threads)
- [ ] Cache miss analysis
- [ ] Bottleneck identification
- [ ] Explanation of non-ideal speedup

**2. Across-Wires Design & Performance (40 points)**
- [ ] Design approach and evolution
- [ ] Batch processing strategy
- [ ] Synchronization and task assignment
- [ ] Performance debugging journey (include Tracy insights!)
- [ ] Speedup graphs (GHC: 1,2,4,8,16 threads)
- [ ] Cache miss analysis
- [ ] Bottleneck identification (synchronization, coherence, imbalance)
- [ ] Explanation of efficiency drop at high thread counts
- [ ] Documentation of calculateRouteCost optimization

**3. Routing Output (2 points)**
- [ ] Visual output for medium_4096.txt, 8 threads
- [ ] Both within-wire and across-wire versions
- [ ] Max occupancy and total cost reported

**4. GHC Experimental Results (20 points)**
- [ ] Total speedup graphs (both modes)
- [ ] Computation speedup graphs (both modes)
- [ ] Cache miss graphs:
  - [ ] Total cache misses vs threads
  - [ ] Per-thread cache misses vs threads
- [ ] Discussion of trends and surprises
- [ ] Correlation with speedup results

**5. Sensitivity Studies (8 points)**
- [ ] SA probability sensitivity (P = 0.01, 0.1, 0.5)
- [ ] Problem size sensitivity (grid size and wire count)
- [ ] Graphs and analysis

**6. PSC Experimental Results (10 points)**
- [ ] Speedup graphs for both modes (16,32,64,128 threads)
- [ ] Comparison with GHC results
- [ ] Discussion of scalability and architecture effects

### **4.2 Report Quality**
- [ ] All graphs properly labeled (axes, legend, title)
- [ ] Consistent formatting and style
- [ ] Clear, concise writing
- [ ] Figures referenced in text
- [ ] Proofreading and spell-check

---

## 🔧 **Phase 5: Code Cleanup & Submission**

### **5.1 Code Quality**
- [ ] Remove debug print statements
- [ ] Clean up commented-out code
- [ ] Verify `make clean` works
- [ ] Verify `make` compiles without warnings
- [ ] Test all command-line arguments
- [ ] Verify output file generation:
  - [ ] occupancy_<input>_<threads>.txt
  - [ ] routes_<input>_<threads>.txt

### **5.2 Testing**
- [ ] Test with all `/code/inputs/testinput/` files
- [ ] Verify correctness with validate.cpp (if provided)
- [ ] Test both -m W and -m A modes
- [ ] Test various batch sizes (-b 1, 2, 4, 8)
- [ ] Test edge cases (1 thread, 16 threads)

### **5.3 Submission Preparation**
- [ ] Form group on Autolab (if working with partner)
- [ ] Run `make handin.tar`
- [ ] Verify handin.tar contains all C++ source files
- [ ] Upload to Autolab
- [ ] Upload report.pdf to Gradescope
- [ ] Select appropriate pages for each question
- [ ] Add teammate on Gradescope (if applicable)

---

## 📅 **Timeline & Prioritization**

### **Week 1: Implementation (Current Week)**
- **Days 1-2:** ✅ Complete across-wire implementation (DONE)
- **Days 3-4:** Implement within-wire parallelization
- **Days 5-6:** Debugging and initial testing

### **Week 2: Experimentation & Analysis**
- **Days 1-2:** GHC experimental data collection (both modes)
- **Day 3:** Sensitivity studies (SA probability, problem size)
- **Days 4-5:** PSC experiments (limited, planned carefully!)
- **Day 6:** Data analysis and graph generation

### **Week 3: Writeup & Submission**
- **Days 1-3:** Draft writeup (design journey, analysis)
- **Day 4:** Generate all graphs and figures
- **Day 5:** Review, polish, proofread
- **Day 6:** Code cleanup and submission
- **Day 7:** BUFFER for unexpected issues

---

## 🎯 **Key Success Metrics**

### **Performance Targets** (Based on Assignment Reference Results)
- **Medium 4096:**
  - 1 thread: ~9-10s baseline
  - 8 threads: ~1.3-1.5s (6-7x speedup)
  - Efficiency at 8 threads: >80%

### **Quality Metrics**
- Total cost should be comparable to reference (within 10%)
- Routing should minimize max occupancy

### **Grading Distribution**
- Within-wires: 20 points
- Across-wires: 40 points
- Routing output: 2 points
- GHC experiments: 20 points
- Sensitivity studies: 8 points
- PSC experiments: 10 points
- **Total: 100 points**

---

## 💡 **Important Reminders**

1. **"The journey matters as much as the destination"**
   - Document what you tried, not just what worked
   - Explain why things didn't work
   - Show your thought process

2. **Measure, Don't Guess**
   - Use Tracy profiler for insights
   - Use `perf stat` for cache analysis
   - Collect data before optimizing

3. **PSC Budget Management**
   - Debug thoroughly on GHC first
   - Plan experiments carefully
   - Limit to 10 runs per day
   - Don't waste allocation time

4. **Synchronization is Critical**
   - Across-wire mode needs careful synchronization
   - Balance between correctness and performance
   - Document your locking strategy

5. **Tracy Profiling Insights**
   - Already identified calculateRouteCost bottleneck
   - Optimized and achieved 11-13% improvement
   - Use for within-wire analysis too

---

## 📚 **Resources**

- **Assignment Handout:** `/home/raj/Documents/Projects/PCA/VLSI_across_wire/asst3_handout.md`
- **OpenMP Tutorial:** https://www.openmp.org/resources/tutorials-articles/
- **LLNL OpenMP Guide:** https://hpc-tutorials.llnl.gov/openmp/
- **PSC Bridges-2 Guide:** https://www.psc.edu/resources/bridges-2/user-guide/
- **Tracy Profiler:** Already set up at `/home/raj/Documents/Projects/system_software/tracy/`
- **Course Policy:** http://www.cs.cmu.edu/~418/academicintegrity.html

---

## ✅ **Current Progress Summary**

**What's Done:**
- Across-wire implementation complete and optimized
- Tracy profiling integrated
- Performance optimizations applied (15-32% improvement)
- Initial benchmarking complete

**What's Next:**
1. Implement within-wire parallelization
2. Collect full experimental data
3. Generate all required graphs
4. Write comprehensive analysis
5. Run PSC experiments
6. Submit!

**Estimated Time Remaining:** 30-40 hours over 2-3 weeks

---

**Good luck! You're making excellent progress! 🚀**
