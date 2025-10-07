/**
 * Parallel VLSI Wire Routing via OpenMP
 * Name 1(andrew_id 1), Name 2(andrew_id 2)
 */

#ifndef __WIREOPT_H__
#define __WIREOPT_H__

#include <omp.h>
#include <cstdint>
#include <vector>
#include <array>
#include <cmath>  // For std::abs
#include <stdexcept>  // For std::logic_error

#define MAX_PTS_PER_WIRE 4
#define COST_REPORT_DEPTH 10

/** README(student):
 We provide two options for validating consistency between wire layout
 and occupancy:
 - After your program is finished and the output written to a file,
   you can run ./validate.py -r <route_file> -c <cost_file>.
 - If you wish to validate your data within the program, or between batches,
   you can create a wr_checker that tracks your data structures:
    wr_checker Checker(wires, occupancy);
   and call its validate() method from your code.
 The struct below is the standard format for wires used by the wire checker.
 It contains a buffer that holds up to four points, and a num_pts field 
 that specifies the number of points.
 Regardless of what representation you use for your wires, you should 
 implement the Wire::to_validate_format method to convert your Wire
 to a validate_wire_t if you wish to use the checker.
*/
struct validate_wire_t {
  uint8_t num_pts;
  struct {
    uint16_t x;
    uint16_t y;
  } p[MAX_PTS_PER_WIRE];
  validate_wire_t &cleanup(void);
  void print_wire(void) const;
};

// Forward declaration of Route so Wire can reference it
struct Route;

struct Wire {
  /** 
   * Point represents a 2D coordinate in the wire routing grid
   */
  struct Point {
    int x, y; 
    
    constexpr Point(int x = 0, int y = 0) : x(x), y(y) {}
    
    constexpr bool operator==(const Point& other) const noexcept {
      return x == other.x && y == other.y; 
    }
    
    constexpr bool operator!=(const Point& other) const noexcept {
      return !(*this == other);
    }
    
    // Manhattan distance between two points
    [[nodiscard]] constexpr int manhattanDistanceTo(const Point& other) const noexcept {
      return std::abs(x - other.x) + std::abs(y - other.y);
    }
  };

  Point start, end; 
  std::array<Point, 2> bends;  // Up to 2 intermediate bend points
  uint8_t num_bends = 0;       // Number of actual bends used (0, 1, or 2)
  
  // Optional: store complete route path (all points from start to end)
  std::vector<Point> route_path;  // Empty if not computed, otherwise full path

  /** 
   * Default constructor creates invalid wire at origin
   */
  Wire() = default;
  
  /**
   * Constructor for straight-line wire (no bends)
   */
  Wire(Point start_pt, Point end_pt) 
    : start(start_pt), end(end_pt), num_bends(0) {}

  /**
   * Validation: checks if wire is valid (non-negative coordinates, valid bend count)
   */
  [[nodiscard]] constexpr bool isValid() const noexcept {
    return num_bends <= 2 && 
           start.x >= 0 && start.y >= 0 && 
           end.x >= 0 && end.y >= 0; 
  }


  
  
  /**
   * Calculate total Manhattan length of the wire route
   */
  [[nodiscard]] constexpr int manhattanLength() const noexcept {
    if (num_bends == 0) {
      return start.manhattanDistanceTo(end);
    }
    
    int total = start.manhattanDistanceTo(bends[0]);
    for (uint8_t i = 1; i < num_bends; ++i) {
      total += bends[i-1].manhattanDistanceTo(bends[i]);
    }
    total += bends[num_bends-1].manhattanDistanceTo(end);
    return total;
  }
  
  /**
   * Get all points in the route (start -> bends -> end)
   */
  [[nodiscard]] std::vector<Point> getRoutePoints() const {
    std::vector<Point> points;
    points.reserve(2 + num_bends);
    
    points.push_back(start);
    for (uint8_t i = 0; i < num_bends; ++i) {
      points.push_back(bends[i]);
    }
    points.push_back(end);
    return points;
  }
  
  /**
   * Check if this is a straight-line wire (no bends)
   */
  [[nodiscard]] constexpr bool isStraightLine() const noexcept {
    return num_bends == 0 && (start.x == end.x || start.y == end.y);
  }

  /**
   * Required conversion method for validation framework
   */
  validate_wire_t to_validate_format() const;
};

/**
 * Route represents a candidate path during optimization phase
 * Lightweight structure for exploring different routing options
 */
struct Route {
  using Point = Wire::Point;
  
  Point start, end;
  std::vector<Point> bends;
  
  Route() = default;
  Route(Point s, Point e) : start(s), end(e) {}
  Route(Point s, Point e, std::vector<Point> b) : start(s), end(e), bends(std::move(b)) {}
  
  std::vector<Point> getKeyPoints() const {
    std::vector<Point> points;
    points.reserve(2 + bends.size());
    
    points.push_back(start);
    for (const auto& bend : bends) {
      points.push_back(bend);
    }
    points.push_back(end);
    return points;
  }
  
  Wire toWire() const {
    Wire wire(start, end);
    wire.num_bends = static_cast<uint8_t>(std::min(bends.size(), size_t(2)));
    for (size_t i = 0; i < wire.num_bends; ++i) {
      wire.bends[i] = bends[i];
    }
    return wire;
  }
  
  std::vector<Point> getAllPoints(int dim_x, int dim_y) const {
    // Pre-validate: Check if start and end are within occupancy matrix bounds
    if (start.x < 0 || start.x >= dim_x || start.y < 0 || start.y >= dim_y) {
      throw std::logic_error("Start point outside occupancy matrix bounds");
    }
    if (end.x < 0 || end.x >= dim_x || end.y < 0 || end.y >= dim_y) {
      throw std::logic_error("End point outside occupancy matrix bounds");
    }
        
    std::vector<Point> points;
    auto key_points = getKeyPoints();
    
    for (size_t i = 1; i < key_points.size(); ++i) {
      const auto& prev = key_points[i-1];
      const auto& curr = key_points[i];
      
      if (prev.x == curr.x) {
        // Vertical segment
        const int step = (curr.y > prev.y) ? 1 : -1;
        
        for (int y = prev.y; y != curr.y; y += step) {
          points.emplace_back(prev.x, y);
        }
      } else if (prev.y == curr.y) {
        // Horizontal segment
        const int step = (curr.x > prev.x) ? 1 : -1;
        
        for (int x = prev.x; x != curr.x; x += step) {
          points.emplace_back(x, prev.y);
        }
      } else {
        throw std::logic_error("Diagonal segments not allowed in routes");
      }
    }
    
    // Add final point (already validated via start/end check)
    if (!key_points.empty()) {
      points.push_back(key_points.back());
    }
    
    return points;
  }
};

struct wr_checker {
  std::vector<Wire> wires;
  std::vector<std::vector<int>> occupancies;
  const int nwires;
  const int dim_x;
  const int dim_y;
  wr_checker(std::vector<Wire> &wires, std::vector<std::vector<int>> &occupancies) 
  : wires(wires), occupancies(occupancies), nwires(wires.size()), dim_x(occupancies[0].size()), dim_y(occupancies.size()) {}
  void validate() const;
};

const char *get_option_string(const char *option_name,
                              const char *default_value);
int get_option_int(const char *option_name, int default_value);
float get_option_float(const char *option_name, float default_value);

#endif
