# BlueSRAM - BSV Wrapper for SRAM macros

BlueSRAM is a wrapper library allowing you to use SRAM macros in your BSV code.

## Interfaces

BlueSRAM can be used with these different interfaces:

a) Unbuffered mode

In essence, you use the macro as it has been generated. If the response method is not enabled on every clock cycle, data may get lost.
This mode adds the least ressources as at most a 2-Bit shift register is added to keep track of in-flight requests.

b) Buffered mode

This mode adds a delay of 1 as well as an (at most) 4-Element FIFO and a 3-Bit counter to keep elements in storage if backpressure arises while still allowing to read one element per clock without the risk of loosing data. The used interface is custom.

## Usage

BlueSRAM provides a unified interface for all types of macros if required. Currently, openRAM and BRAMs are supported. openRAM macros directly use the unified interface. BRAMs can be wrapped. The use of a similar interface allows for rapid exchange of macros.

The interface definition looks like this:
```
interface RIfc#(numeric type addrwidth, numeric type datawidth);
    method Action request(Bit#(addrwidth) addr);
    method ActionValue#(Bit#(datawidth)) response;
endinterface

interface WIfc#(numeric type addrwidth, numeric type datawidth, numeric type ena_width);
    method Action request(Bit#(addrwidth) addr, Bit#(datawidth) din, Bit#(ena_width) mask);
endinterface

interface RWIfc#(numeric type addrwidth, numeric type datawidth, numeric type ena_width);
    method Action request(Bit#(addrwidth) addr, Bit#(datawidth) din, Bit#(ena_width) mask, Bool write_en);
    method ActionValue#(Bit#(datawidth)) response;
endinterface

// main interface for openRAM
interface OpenRAMIfc#(numeric type rd_ports, numeric type wr_ports, numeric type rw_ports, numeric type addrwidth, numeric type datawidth, numeric type ena_width);
        interface Vector#(rd_ports, RIfc#(addrwidth, datawidth)) r;
        interface Vector#(wr_ports, WIfc#(addrwidth, datawidth, ena_width)) w;
        interface Vector#(rw_ports, RWIfc#(addrwidth, datawidth, ena_width)) rw;
endinterface
```

Read, write and read/write ports are separated as they provide different functionality.
For openRAM, instantiate a macro by utilizing the typeclass. Read the openRAM usage section for info on how to generate the wrappers.

```
OpenRAMIfc#(1, 1, 0, 10, 8, 0) dut <- mkOpenRAM(True);
```

For BRAMs, instantiate a BRAM and call the wrapper:
```
BRAM2Port#(Bit#(15), Bit#(16)) bram <- mkBRAM2Server (cfg) ;
OpenRAMIfc#(0, 0, 1, 15, 16, 0) dut <- mkOpenRamBRAMDP(bram);
```
Multiple wrappers are available and ports can be treated as r, w and rw ports as configured.

## Usage (openRAM)

Call `create_wrappers_openram.py` and point it to the directory with your macros. The script will create wrappers for all macros in that directory.

To instantiate a macro, use the typeclass for automatic inference:

```
OpenRAMIfc#(<read_ports>, <write_ports>, <rw_ports>, <addr_width>, <data_width>, <enable_width>) dut <- mkOpenRAM(<add_fifo_buffer>);
```

The provided information will be used to select the correct macro. If requested, a FIFO is added to support backpressure. This is similar to BSV BRAMs.

A limitation of the current scheme is that if you have macros with a similar interface but varying depths (e.g. a 1024-Word macro and a 1000-Word macro with all other settings untouched), no disambiguation is possible. This limitation results from the simulation models always assuming a completely filled address space. As we extract all information from the simulation models, we are unaware of the memory depth.

Additionally, even if no FIFO is requested, the BRAM output is always registered. If no register was inserted, certain actions would result in the propagation of X values in questa since the models simulate hold timings.

For simulation, insert `timescale 1ns / 1ps` into your simulation model.

In case of issues, feedback or willingness to add own contributions, contact @ms.

## Usage (SRAM22)

SRAM22 reuses most OpenRAM code. Call `create_wrappers_openram.py` with the `--sram22` flag and point it to the directory with your macros.
The interface is similar to OpenRAM, but the typeclass name is different:


```
OpenRAMIfc#(0, 0, 1, <addr_width>, <data_width>, <enable_width>) dut <- mkSRAM22(<add_fifo_buffer>);
```

Since SRAM22 only supports RW single ported memories, the first three parameters of the interface never change.
