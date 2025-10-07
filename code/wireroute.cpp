/**
 * Parallel VLSI Wire Routing via OpenMP
 * Name 1(andrew_id 1), Name 2(andrew_id 2)
 */

#include "wireroute.h"

#include <algorithm>
#include <iostream>
#include <fstream>
#include <iomanip>
#include <chrono>
#include <string>
#include <vector>
#include <random>

#include <unistd.h>
#include <omp.h>

using std::vector;

// Function to generate all possible paths for a wire

int calculateRouteCost(const Route& route, const std::vector<std::vector<int>>& occupancy){
  // Get all the points in the route, then do incremental cost calculation 

  auto all_points = route.getAllPoints(occupancy[0].size(), occupancy.size());

  int incremental_cost = 0; 

  // Loop through all the points, add the incremental cost to the occupancy grid 
  for(const auto& point: all_points){
    int current_occupancy = occupancy[point.y][point.x];

    int old_cost = current_occupancy * current_occupancy;
    int new_cost = (current_occupancy + 1) * (current_occupancy + 1);
    incremental_cost += (new_cost - old_cost);
  }

  return incremental_cost;
}

void updateOccupancyGrid(const Route& route, std::vector<std::vector<int>>& occupancy){
    auto all_points = route.getAllPoints(occupancy[0].size(), occupancy.size());
    for(const auto& point : all_points){
        occupancy[point.y][point.x]++;
    }
    return; 
}

vector<Route> enumerate_candidates(Wire::Point start, Wire::Point end){

  vector <Route> routes; 

  // Case 1: Direct path (no bends)
  // Calculate dx, dy 
  const int dx = end.x - start.x; 
  const int dy = end.y - start.y; 

  // Check if there is a direct horizontal/vertical path 
  if(dx == 0 || dy ==0){
    routes.emplace_back(start, end); 
    return routes; 
  }
  // Case 2: One bend (L or Z shape)

  // Two possible one-bend routes 
  // Route 1: Horizontal then Vertical 
  routes.emplace_back(start, end, std::vector<Wire::Point>{Wire::Point(end.x, start.y)});

  // Route 2: Vertical then Horizontal
  routes.emplace_back(start, end, std::vector<Wire::Point>{Wire::Point(start.x, end.y)});

  // Case 3: Two bends (U or S shape)
  for(int x = std::min(start.x, end.x) + 1; x < std::max(start.x, end.x); ++x){
    routes.emplace_back(start, end, std::vector<Wire::Point>{Wire::Point(x, start.y), Wire::Point(x, end.y)});
  }

  for(int y = std::min(start.y, end.y) + 1; y < std::max(start.y, end.y); ++y){
    routes.emplace_back(start, end, std::vector<Wire::Point>{Wire::Point(start.x, y), Wire::Point(end.x, y)});
  }

  return routes;
}

void print_stats(const std::vector<std::vector<int>>& occupancy) {
  int max_occupancy = 0;
  long long total_cost = 0;

  for (const auto& row : occupancy) {
    for (const int count : row) {
      max_occupancy = std::max(max_occupancy, count);
      total_cost += count * count;
    }
  }

  std::cout << "Max occupancy: " << max_occupancy << '\n';
  std::cout << "Total cost: " << total_cost << '\n';
}

void write_output(const std::vector<Wire>& wires, const int num_wires, const std::vector<std::vector<int>>& occupancy, const int dim_x, const int dim_y, const int num_threads, std::string input_filename) {
  // Extract just the filename without path and extension
  size_t last_slash = input_filename.find_last_of("/\\");
  if (last_slash != std::string::npos) {
    input_filename = input_filename.substr(last_slash + 1);
  }
  if (std::size(input_filename) >= 4 && input_filename.substr(std::size(input_filename) - 4) == ".txt") {
    input_filename.resize(std::size(input_filename) - 4);
  }

  const std::string occupancy_filename = "occupancy_" + input_filename + "_" + std::to_string(num_threads) + ".txt";
  const std::string wires_filename = "routes_" + input_filename + "_" + std::to_string(num_threads) + ".txt";

  std::ofstream out_occupancy(occupancy_filename, std::fstream::out);
  if (!out_occupancy) {
    std::cerr << "Unable to open file: " << occupancy_filename << '\n';
    exit(EXIT_FAILURE);
  }

  out_occupancy << dim_x << ' ' << dim_y << '\n';
  for (const auto& row : occupancy) {
    for (const int count : row) {
      out_occupancy << count << ' ';
    }
    out_occupancy << '\n';
  }

  out_occupancy.close();

  std::ofstream out_wires(wires_filename, std::fstream:: out);
  if (!out_wires) {
    std::cerr << "Unable to open file: " << wires_filename << '\n';
    exit(EXIT_FAILURE);
  }

  out_wires << dim_x << ' ' << dim_y << '\n' << num_wires << '\n';

  // for (const auto& [start_x, start_y, end_x, end_y, bend1_x, bend1_y] : wires) {

  for (const auto& wire : wires) {
    // Write all route points for this wire
    // Use route_path if available, otherwise fall back to getRoutePoints()
    const auto& route_points = wire.route_path.empty() ? wire.getRoutePoints() : wire.route_path;
    
    for (size_t i = 0; i < route_points.size(); ++i) {
      out_wires << route_points[i].x << ' ' << route_points[i].y;
      if (i < route_points.size() - 1) {
        out_wires << ' ';
      }
    }
    out_wires << '\n';
  }

  out_wires.close();
}

int main(int argc, char *argv[]) {
  const auto init_start = std::chrono::steady_clock::now();

  std::string input_filename;
  int num_threads = 0;
  double SA_prob = 0.1;
  int SA_iters = 5;
  char parallel_mode = '\0';
  int batch_size = 1;

  int opt;
  while ((opt = getopt(argc, argv, "f:n:p:i:m:b:")) != -1) {
    switch (opt) {
      case 'f':
        input_filename = optarg;
        break;
      case 'n':
        num_threads = atoi(optarg);
        break;
      case 'p':
        SA_prob = atof(optarg);
        break;
      case 'i':
        SA_iters = atoi(optarg);
        break;
      case 'm':
        parallel_mode = *optarg;
        break;
      case 'b':
        batch_size = atoi(optarg);
        break;
      default:
        std::cerr << "Usage: " << argv[0] << " -f input_filename -n num_threads [-p SA_prob] [-i SA_iters] -m parallel_mode -b batch_size\n";
        exit(EXIT_FAILURE);
    }
  }

  // Check if required options are provided
  if (empty(input_filename) || num_threads <= 0 || SA_iters <= 0 || (parallel_mode != 'A' && parallel_mode != 'W') || batch_size <= 0) {
    std::cerr << "Usage: " << argv[0] << " -f input_filename -n num_threads [-p SA_prob] [-i SA_iters] -m parallel_mode -b batch_size\n";
    exit(EXIT_FAILURE);
  }

  std::cout << "Number of threads: " << num_threads << '\n';
  std::cout << "Simulated annealing probability parameter: " << SA_prob << '\n';
  std::cout << "Simulated annealing iterations: " << SA_iters << '\n';
  std::cout << "Input file: " << input_filename << '\n';
  std::cout << "Parallel mode: " << parallel_mode << '\n';
  std::cout << "Batch size: " << batch_size << '\n';

  std::ifstream fin(input_filename);

  if (!fin) {
    std::cerr << "Unable to open file: " << input_filename << ".\n";
    exit(EXIT_FAILURE);
  }

  int dim_x, dim_y;
  int num_wires;

  /* Read the grid dimension and wire information from file */
  fin >> dim_x >> dim_y >> num_wires;

  std::vector<Wire> wires(num_wires);
  std::vector occupancy(dim_y, std::vector<int>(dim_x));

  // for (auto& wire : wires) {
  //   fin >> wire.start_x >> wire.start_y >> wire.end_x >> wire.end_y;
  //   wire.bend1_x = wire.start_x;
  //   wire.bend1_y = wire.start_y;
  // }

  for (auto& wire : wires) {
    fin >> wire.start.x >> wire.start.y >> wire.end.x >> wire.end.y;
    wire.num_bends = 0;  // Initialize with no bends
  }

  /* Initialize any additional data structures needed in the algorithm */

  const double init_time = std::chrono::duration_cast<std::chrono::duration<double>>(std::chrono::steady_clock::now() - init_start).count();
  std::cout << "Initialization time (sec): " << std::fixed << std::setprecision(10) << init_time << '\n';

  const auto compute_start = std::chrono::steady_clock::now();


  /** 
   * Implement the wire routing algorithm here
   * Feel free to structure the algorithm into different functions
   * Don't use global variables.
   * Use OpenMP to parallelize the algorithm. 
   */

  // Single-threaded implementation with simulated annealing as per assignment
  if (parallel_mode == 'A'){
    //Across WIRE PARALLELIZATION

    omp_set_num_threads(num_threads);

    int num_batches = (num_wires + batch_size - 1)/batch_size; 
    int num_batches_default = num_batches; 
    int batch_idx = 0; 

    // Phase 1: Initial placement with batching 
    #pragma omp parallel
    {
      while(batch_idx < num_batches_default){

        // Single thread pipeline 
        int batch_start, batch_end; 

        // Grab a batch 
        #pragma omp critical
        {
          batch_start = (batch_idx) * batch_size; 
          batch_idx++;
          batch_end = std::min(batch_start + batch_size - 1, num_wires - 1);
        }

        // Phase 1: Find initial routes for wires in this batch 
        for(int wire_idx = batch_start; wire_idx<=batch_end; wire_idx++){
          auto candidates = enumerate_candidates(wires[wire_idx].start, wires[wire_idx].end);

          Route best_route = candidates[0];
          int min_cost = calculateRouteCost(best_route, occupancy);

          for(size_t i = 1; i < candidates.size(); ++i){
            int cost = calculateRouteCost(candidates[i], occupancy);
            if(cost < min_cost){
              min_cost = cost; 
              best_route = candidates[i];
            }
            
          }
          wires[wire_idx].route_path = best_route.getAllPoints(dim_x, dim_y);
        }
        // Phase 2: Update the occupancy matrix 
        for(int wire_idx = batch_start; wire_idx<=batch_end; ++wire_idx){
          // Loop through all the points in the route path of the wire 
          for(const auto& point: wires[wire_idx].route_path){
            #pragma omp atomic
              occupancy[point.y][point.x]++;
          }       
        }
      }
    }
    
    
    for(int iter = 0; iter<SA_iters; ++iter){
      
      std::cout <<"SA Iteration "<<(iter+1)<<"/"<<SA_iters<<std::endl; 

      // Start Phase 2: Simulated annealing iterations with batching
      int batch_idx = 0; 

      #pragma omp parallel
      {
        std::random_device rd; 
        std::mt19937 gen(rd() + omp_get_thread_num());
        std::uniform_real_distribution<> prob_dist(0.0, 1.0);

        while(batch_idx < num_batches_default){

          // Single thread pipeline 
          int batch_start, batch_end; 

          #pragma omp critical
          {
            batch_start = batch_idx * batch_size; 
            batch_idx++; 
            batch_end = std::min(batch_start + batch_size - 1, num_wires - 1);
          }
          
          // Phase 0: Remove the current batch routes from occupancy matrix so that each wire in the batch compares against the same matrix 
          for(int wire_idx = batch_start; wire_idx<=batch_end; ++wire_idx){
            for(const auto& point: wires[wire_idx].route_path){
              #pragma omp atomic 
              occupancy[point.y][point.x]--;
            }
          }

          // Phase 1: Find initial routes for wires in this batch 
          for(int wire_idx = batch_start; wire_idx<=batch_end; wire_idx++){
            auto candidates = enumerate_candidates(wires[wire_idx].start, wires[wire_idx].end);

            Route best_route = candidates[0];
            int min_cost = calculateRouteCost(best_route, occupancy);

            for(size_t i = 1; i < candidates.size(); ++i){
              int cost = calculateRouteCost(candidates[i], occupancy);
              if(cost < min_cost){
                min_cost = cost; 
                best_route = candidates[i];
              }
              
            }

            Route selected_route = best_route; 
            
            if(candidates.size()>1 && prob_dist(gen) < SA_prob){
              std::uniform_int_distribution<> route_dist(0, candidates.size()-1); 
              selected_route = candidates[route_dist(gen)];            
            }

            wires[wire_idx].route_path = selected_route.getAllPoints(dim_x, dim_y);
          }
          
          // Phase 2: Update the occupancy matrix 
          for(int wire_idx = batch_start; wire_idx<=batch_end; ++wire_idx){
            // Loop through all the points in the route path of the wire 
            for(const auto& point: wires[wire_idx].route_path){
              #pragma omp atomic
                occupancy[point.y][point.x]++;
            }       
          }
        }
      }
    }
  }

  const double compute_time = std::chrono::duration_cast<std::chrono::duration<double>>(std::chrono::steady_clock::now() - compute_start).count();
  std::cout << "Computation time (sec): " << compute_time << '\n';

  /* Write wires and occupancy matrix to files */

  print_stats(occupancy);
  write_output(wires, num_wires, occupancy, dim_x, dim_y, num_threads, input_filename);
}

validate_wire_t Wire::to_validate_format() const {
  validate_wire_t result;
  auto route_points = getRoutePoints();
  
  result.num_pts = static_cast<uint8_t>(std::min(route_points.size(), 
                                                 static_cast<size_t>(MAX_PTS_PER_WIRE)));
  
  for (size_t i = 0; i < result.num_pts; ++i) {
    result.p[i].x = static_cast<uint16_t>(route_points[i].x);
    result.p[i].y = static_cast<uint16_t>(route_points[i].y);
  }
  
  return result;
}
