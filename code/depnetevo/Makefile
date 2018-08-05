UNAME := $(shell uname)

SNAP_PATH = ../Snap-3.0
CXXFLAGS =	-O2 -march=native -fpermissive  -Wall -fopenmp -fmessage-length=0 -std=c++11 -I$(SNAP_PATH)/glib-core -I$(SNAP_PATH)/snap-core
LIBS = $(SNAP_PATH)/snap-core/Snap.o -lgomp -lpthread 

OBJS =		depnetevo.o
MAIN = depnetevo.cpp
TARGET = depnetevo

$(TARGET):	$(OBJS)
	$(CXX) -o  $(TARGET) $(OBJS)  $(LIBS) 
	
all:	$(TARGET)

clean:
	rm -f $(OBJS) $(TARGET) 
