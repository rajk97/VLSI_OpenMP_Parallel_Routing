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
CXXFLAGS = -Wall -O3 -std=c++17 -m64 -I. -fopenmp -Wno-unknown-pragmas $(TRACY_FLAGS)

all: $(APP_NAME)

$(APP_NAME): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $(OBJS) $(TRACY_LIBS)

TracyClient.o: TracyClient.cpp
	$(CXX) $(CXXFLAGS) -c TracyClient.cpp -o TracyClient.o

%.o: %.cpp %.h
	$(CXX) $(CXXFLAGS) -c $<

clean:
	/bin/rm -rf *~ *.o $(APP_NAME) *.class
