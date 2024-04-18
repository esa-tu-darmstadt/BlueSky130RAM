package OpenRAMIfc;

import Vector::*;

// Interfaces for lowlevel wrappers with explicit enable signal
interface LL_RIfc#(numeric type addrwidth, numeric type datawidth);
    method Action request(Bit#(addrwidth) addr);
    method Action ena(Bool en);
    method Bit#(datawidth) response;
endinterface

interface LL_WIfc#(numeric type addrwidth, numeric type datawidth, numeric type ena_width);
    method Action request(Bit#(addrwidth) addr, Bit#(datawidth) din, Bit#(ena_width) mask);
    method Action ena(Bool en);
endinterface

interface LL_RWIfc#(numeric type addrwidth, numeric type datawidth, numeric type ena_width);
    method Action request(Bit#(addrwidth) addr, Bit#(datawidth) din, Bit#(ena_width) mask, Bool write_en);
    method Action ena(Bool en);
    method Bit#(datawidth) response;
endinterface

interface LL_RWIfc22#(numeric type addrwidth, numeric type datawidth, numeric type ena_width);
    method Action request(Bit#(addrwidth) addr, Bit#(datawidth) din, Bit#(ena_width) mask, Bool write_en);
    method Bit#(datawidth) response;
endinterface

// Interfaces for a single port for higher-level wrappers
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

endpackage