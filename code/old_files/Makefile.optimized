# Optimized Makefile for Intel i9-14900KF
# Adds architecture-specific optimizations beyond base -O3

APP_NAME=wireroute

# Tracy profiler configuration
TRACY_DIR = /home/raj/Documents/Projects/system_software/tracy
TRACY_ENABLED ?= 0

OBJS=wireroute.o validate.o

# Add Tracy client if enabled
ifeq ($(TRACY_ENABLED), 1)
    OBJS += TracyClient.o
    TRACY_FLAGS = -DTRACY_ENABLE -I$(TRACY_DIR)/public
    TRACY_LIBS = -lpthread -ldl
else
    TRACY_FLAGS =
    TRACY_LIBS =
endif

CXX = g++

# BASE FLAGS (original)
BASE_FLAGS = -Wall -O3 -std=c++17 -m64 -I. -fopenmp -Wno-unknown-pragmas

# AGGRESSIVE OPTIMIZATIONS for Intel i9-14900KF
# -march=native: Use all CPU instructions (AVX2, AVX-VNNI, etc.)
# -flto: Link-time optimization (whole program optimization)
# -ffast-math: Aggressive floating-point optimizations
# -funroll-loops: Unroll loops for better performance
# -finline-functions: Aggressive function inlining
# -ftree-vectorize: Explicit vectorization (redundant with O3 but explicit)
# -fno-signed-zeros -fno-trapping-math: Additional fast-math optimizations
OPT_FLAGS = -march=native -flto -ffast-math -funroll-loops -finline-functions -ftree-vectorize

# Combine flags
CXXFLAGS = $(BASE_FLAGS) $(OPT_FLAGS) $(TRACY_FLAGS)
LDFLAGS = -flto -fopenmp

all: $(APP_NAME)

$(APP_NAME): $(OBJS)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $@ $(OBJS) $(TRACY_LIBS)

TracyClient.o: TracyClient.cpp
	$(CXX) $(CXXFLAGS) -c TracyClient.cpp -o TracyClient.o

%.o: %.cpp %.h
	$(CXX) $(CXXFLAGS) -c $<

clean:
	/bin/rm -rf *~ *.o $(APP_NAME) *.class

# Show optimization flags being used
show-flags:
	@echo "Compiler: $(CXX)"
	@echo "Base flags: $(BASE_FLAGS)"
	@echo "Optimization flags: $(OPT_FLAGS)"
	@echo "Tracy flags: $(TRACY_FLAGS)"
	@echo "Final CXXFLAGS: $(CXXFLAGS)"
