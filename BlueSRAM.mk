MAKEPATH := $(dir $(lastword $(MAKEFILE_LIST)))
MODULENAME := BlueBRAM
MODULEPATH := $(MAKEPATH)src
EXTRA_BSV_LIBS += $(MODULEPATH)

RUN_FLAGS+= -suppress 3009
-include openram.mk

$(info Adding $(MODULENAME) from $(MODULEPATH))