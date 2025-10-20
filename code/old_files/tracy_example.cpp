/**
 * Example of how to add Tracy profiling to wireroute.cpp
 * 
 * This file shows you where and how to add Tracy zones
 * to profile your OpenMP wire routing code.
 */

// At the top of wireroute.cpp, add:
#ifdef TRACY_ENABLE
#include "tracy/public/Tracy.hpp"
#endif

// Then instrument your code like this:

// Example 1: Profile the entire main computation
void example_main_computation() {
#ifdef TRACY_ENABLE
    ZoneScoped;  // Automatically tracks this function
#endif
    
    // your computation code...
}

// Example 2: Profile sections within your across-wires loop
void example_across_wires_parallel() {
    omp_set_num_threads(num_threads);
    
    #pragma omp parallel
    {
#ifdef TRACY_ENABLE
        ZoneScopedN("Parallel Region");  // Named zone
#endif
        
        while(batch_idx < num_batches_default) {
#ifdef TRACY_ENABLE
            ZoneScopedN("Batch Processing");
#endif
            
            // Critical section for batch grabbing
            #pragma omp critical
            {
#ifdef TRACY_ENABLE
                ZoneScopedN("Grab Batch");
#endif
                batch_start = batch_idx * batch_size; 
                batch_idx++;
                batch_end = std::min(batch_start + batch_size - 1, num_wires - 1);
            }
            
            // Phase 0: Remove old routes
            {
#ifdef TRACY_ENABLE
                ZoneScopedN("Phase 0 - Remove Routes");
#endif
                for(int wire_idx = batch_start; wire_idx<=batch_end; ++wire_idx){
                    // ... removal code ...
                }
            }
            
            // Phase 1: Find new routes  
            {
#ifdef TRACY_ENABLE
                ZoneScopedN("Phase 1 - Find Routes");
#endif
                for(int wire_idx = batch_start; wire_idx<=batch_end; wire_idx++){
                    // ... route finding code ...
                }
            }
            
            // Phase 2: Update occupancy
            {
#ifdef TRACY_ENABLE
                ZoneScopedN("Phase 2 - Update Occupancy");
#endif
                for(int wire_idx = batch_start; wire_idx<=batch_end; ++wire_idx){
                    // ... occupancy update code ...
                }
            }
        }
    }
}

// Example 3: Profile individual expensive functions
int example_calculate_cost(const Route& route, const std::vector<std::vector<int>>& occupancy) {
#ifdef TRACY_ENABLE
    ZoneScopedN("Calculate Route Cost");
#endif
    
    // ... cost calculation ...
    return 0;
}

/**
 * HOW TO BUILD AND USE:
 * 
 * 1. Build WITHOUT Tracy (normal):
 *    make clean && make
 * 
 * 2. Build WITH Tracy (profiling enabled):
 *    make clean && make TRACY_ENABLED=1
 * 
 * 3. Run your program:
 *    ./wireroute -f inputs/timeinput/easy_4096.txt -n 4 -i 5 -m A -b 1
 * 
 * 4. This will generate a trace file: trace-XXXX.tracy
 * 
 * 5. View the trace with Tracy profiler:
 *    /home/raj/Documents/Projects/system_software/tracy/profiler/build/Tracy-profiler trace-XXXX.tracy
 * 
 * NOTE: The Tracy profiler GUI requires CMake 3.25+. We'll set that up separately,
 * or you can use the online viewer at: https://tracy.nereid.pl/
 */
