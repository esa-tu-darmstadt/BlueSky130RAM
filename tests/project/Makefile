###
# DO NOT CHANGE
###
TOP_MODULE=mkTestProj
TESTBENCH_MODULE=mkTestbench
IGNORE_MODULES=mkTestbench mkTestsMainTest
MAIN_MODULE=TestProj
TESTBENCH_FILE=src/Testbench.bsv


# Initialize
-include .bsv_tools
ifndef BSV_TOOLS
$(error BSV_TOOLS is not set (Check .bsv_tools or specify it through the command line))
endif
VIVADO_ADD_PARAMS := ''
CONSTRAINT_FILES := ''
EXTRA_BSV_LIBS:=
EXTRA_LIBRARIES:=
RUN_FLAGS:=

PROJECT_NAME=TestProj

ifeq ($(RUN_TEST),)
RUN_TEST=TestsMainTest
endif

# Default flags
EXTRA_FLAGS=-D "RUN_TEST=$(RUN_TEST)" -D "TESTNAME=mk$(RUN_TEST)"
EXTRA_FLAGS+=-show-schedule -keep-fires -D "BSV_TIMESCALE=1ns/1ps"

###
# User configuration
###


ifeq ($(GUARD),1)
	EXTRA_FLAGS+=-D GUARDED=1
endif
ifeq ($(RAM),SRAM22)
	EXTRA_FLAGS+=-D SRAM22=1
endif
ifeq ($(RAM),OPENRAM)
	EXTRA_FLAGS+=-D OPENRAM=1
endif
ifeq ($(RAM),GF22)
	EXTRA_FLAGS+=-D GF22=1
endif
ifeq ($(RAM),BRAMDP)
	EXTRA_FLAGS+=-D BRAMDP=1
endif
ifeq ($(RAM),BRAMSP)
	EXTRA_FLAGS+=-D BRAMSP=1
endif
ifeq ($(RAM),BRAMDPBE)
	EXTRA_FLAGS+=-D BRAMDPBE=1
endif
ifeq ($(RAM),BRAMSPBE)
	EXTRA_FLAGS+=-D BRAMSPBE=1
endif
ifeq ($(RAM),GF22DP)
	EXTRA_FLAGS+=-D GF22DP=1 -D GF22=1
endif
ifeq ($(RAM),GF22DPBE)
	EXTRA_FLAGS+=-D GF22DPBE=1 -D GF22=1
endif
ifeq ($(RAM),GF22SP)
	EXTRA_FLAGS+=-D GF22SP=1 -D GF22=1
endif
ifeq ($(RAM),GF22SPBE)
	EXTRA_FLAGS+=-D GF22SPBE=1 -D GF22=1
endif
ifeq ($(RAM),DFFRAM)
	EXTRA_FLAGS+=-D DFFRAM=1
endif

ifeq ($(TEST_W),1)
	EXTRA_FLAGS+=-D TEST_W=1
endif
ifeq ($(TEST_R),1)
	EXTRA_FLAGS+=-D TEST_R=1
endif

EXTRA_FLAGS+=-D ADDR_WIDTH=$(AW) -D DATA_WIDTH=$(DW) -D R_PORTS=$(P_R) -D W_PORTS=$(P_W) -D RW_PORTS=$(P_RW) -D STROBES=$(STRB) -D WORDS=$(WORDS) -D BITLINE=$(BITLINE) -D MUX=$(MUX) -D LATCHED=$(LATCHED)


# Comment the following line if -O3 should be used during compilation
# Keep uncommented for short running simulations
CXX_NO_OPT := 1

# Any additional files added during compilation
# For instance for BDPI or Verilog/VHDL files for simulation
# CPP_FILES += $(current_dir)/src/mem_sim.cpp

# Custom defines added to compile steps
# EXTRA_FLAGS+=-D "BENCHMARK=1"

# Flags added to simulator execution
RUN_FLAGS+=+bscvcd -suppress 3009

# Add additional parameters for IP-XACT generation. Passed directly to Vivado.
# Any valid TCL during packaging is allowed
# Typically used to fix automatic inference for e.g. clock assignments
# VIVADO_ADD_PARAMS += 'ipx::associate_bus_interfaces -busif M_AXI -clock sconfig_axi_aclk [ipx::current_core]'

# Add custom constraint files, Syntax: Filename,Load Order
# CONSTRAINT_FILES += "$(PWD)/constraints/custom.xdc,LATE"

# Do not change: Load libraries such as BlueAXI or BlueLib
ifneq ("$(wildcard $(PWD)/libraries/*/*.mk)", "")
include $(PWD)/libraries/*/*.mk
endif

# Do not change: Include base makefile
include $(BSV_TOOLS)/scripts/rules.mk
