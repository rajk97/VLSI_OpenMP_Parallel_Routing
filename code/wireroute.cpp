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

#include <unistd.h>
#include <omp.h>

using std::vector;

// Function to generate all possible paths for a wire

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
  if (std::size(input_filename) >= 4 && input_filename.substr(std::size(input_filename) - 4) == ".txt") {
    input_filename.resize(std::size(input_filename) - 4);
  }

  const std::string occupancy_filename = input_filename + "_occupancy_" + std::to_string(num_threads) + ".txt";
  const std::string wires_filename = input_filename + "_wires_" + std::to_string(num_threads) + ".txt";

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
    
    out_wires << wire.start.x << ' ' << wire.start.y << ' ' << wire.bend1.x << ' ' << wire.bend1.y << ' ';

    if (wire.start.y == wire.bend1.y) {
    // first bend was horizontal

      if (wire.end.x != wire.bend1.x) {
        // two bends

        out_wires << wire.bend1.x << ' ' << wire.end.y << ' ';
      }
    } else if (wire.start.x == wire.bend1.x) {
      // first bend was vertical

      if (wire.end.y != wire.bend1.y) {
        // two bends

        out_wires << wire.end.x << ' ' << wire.bend1.y << ' ';
      }
    }
    out_wires << wire.end.x << ' ' << wire.end.y << '\n';
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

  //  The following is a only single threaded implmentation without using OpenMP principles 

  // Start with wire 1, generate all possible paths, pick the one with least cost 
  // Access the first wire
  Wire& first_wire = wires[0];

  // Example: Print the start and end points of the first wire
  // std::cout << "First wire starts at (" << first_wire.start_x << ", " << first_wire.start_y << ") "
  //       << "and ends at (" << first_wire.end_x << ", " << first_wire.end_y << ").\n";

  std::cout << "First wire starts at (" << first_wire.start.x << ", " << first_wire.start.y << ") "
      << "and ends at (" << first_wire.end.x << ", " << first_wire.end.y << ").\n";

  // Generate all possible paths for the first wire 



  const double compute_time = std::chrono::duration_cast<std::chrono::duration<double>>(std::chrono::steady_clock::now() - compute_start).count();
  std::cout << "Computation time (sec): " << compute_time << '\n';

  /* Write wires and occupancy matrix to files */

  print_stats(occupancy);
  write_output(wires, num_wires, occupancy, dim_x, dim_y, num_threads, input_filename);
}

validate_wire_t Wire::to_validate_format(void) const {
  /* TODO(student): Implement this if you want to use the wr_checker. */
  /* See wireroute.h for details on validate_wire_t. */
  throw std::logic_error("to_validate_format not implemented.");
}
