MAKEPATH := $(dir $(lastword $(MAKEFILE_LIST)))
MODULENAME := BlueBRAM
MODULEPATH := $(MAKEPATH)src
EXTRA_BSV_LIBS += $(MODULEPATH)

ifeq ($(SIM_TYPE), VERILOG)
RUN_FLAGS+= -suppress 3009
-include $(MAKEPATH)openram.files
-include $(MAKEPATH)sram22.files
endif

$(info Adding $(MODULENAME) from $(MODULEPATH))