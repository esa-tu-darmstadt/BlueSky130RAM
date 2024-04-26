package WrapBRAMAsOpenRAM;

import OpenRAMIfc::*;
import Vector::*;
import ClientServer::*;
import GetPut::*;
import BRAM::*;

module mkOpenRamBRAMByteEnDP#(BRAM2PortBE#(addr, data, ena) inst) (OpenRAMIfc#(num_r, num_w, num_rw, addr_width, bus, ena)) provisos (
    Add#(num_r, num_w, a),
    Add#(a, num_rw, b), 
    Add#(b, _a, 2), // GF22 macros have two ports, do not exceed that
    Bits#(addr, addr_width),
    Bits#(data, bus)

);
    // track which port is currently mapped
    Integer current_port = 0;

    Vector#(num_r, RIfc#(addr_width, bus)) r_loc = ?;
    Vector#(num_w, WIfc#(addr_width, bus, ena)) w_loc = ?;
    Vector#(num_rw, RWIfc#(addr_width, bus, ena)) rw_loc = ?;

    // map ports to openSRAM iface
    for (Integer i= 0; i < valueOf(num_r); i=i+1) begin
        let p = current_port == 0 ? inst.portA: inst.portB;
        r_loc[i] = (interface RIfc;
            method Action request(Bit#(addr_width) addr);
                p.request.put(BRAMRequestBE {
                    address: unpack(addr),
                    writeen: 0,
                    responseOnWrite: False
                });
            endmethod
            method ActionValue#(Bit#(bus)) response;
                let v <- p.response.get;
                return pack(v);
            endmethod
        endinterface);
        current_port = current_port + 1;
    end

    for (Integer i= 0; i < valueOf(num_w); i=i+1) begin
        let p = current_port == 0 ? inst.portA: inst.portB;
        w_loc[i] = (interface WIfc;
            method Action request(Bit#(addr_width) addr, Bit#(bus) din, Bit#(ena) mask);
                p.request.put(BRAMRequestBE {
                    address: unpack(addr),
                    writeen: mask,
                    datain: unpack(din),
                    responseOnWrite: False
                });
            endmethod
        endinterface);
        current_port = current_port + 1;
    end

    for (Integer i= 0; i < valueOf(num_rw); i=i+1) begin
        let p = current_port == 0 ? inst.portA: inst.portB;
        rw_loc[0] = (interface RWIfc;
            method Action request(Bit#(addr_width) addr, Bit#(bus) din, Bit#(ena) mask, Bool write_en);
                p.request.put(BRAMRequestBE {
                    address: unpack(addr),
                    writeen: write_en ? mask : 0,
                    datain: unpack(din),
                    responseOnWrite: False
                });
            endmethod
            method ActionValue#(Bit#(bus)) response;
                actionvalue
                    let v <- p.response.get;
                    return pack(v);
                endactionvalue
            endmethod
        endinterface);
        current_port = current_port + 1;
    end

    interface r = r_loc;
    interface w = w_loc;
    interface rw = rw_loc;

endmodule

// same for the single-ported macro, this only supports 1 rw port since a read-only or write-only SRAM macro makes no sense
module mkOpenRamBRAMByteEnSP#(BRAM1PortBE#(addr_t, data_t, ena) inst) (OpenRAMIfc#(0, 0, 1, addr_width, bus, ena)) provisos (
    Bits#(addr_t, addr_width),
    Bits#(data_t, bus)
);
    Vector#(num_rw, RWIfc#(addr_width, bus, ena)) rw_loc = ?;

    // map ports to openSRAM iface
    rw_loc[0] = (interface RWIfc;
        method Action request(Bit#(addr_width) addr, Bit#(bus) din, Bit#(ena) mask, Bool write_en);
            inst.portA.request.put(BRAMRequestBE {
                address: unpack(addr),
                writeen: write_en ? mask : 0,
                datain: unpack(din),
                responseOnWrite: False
            });
        endmethod
        method ActionValue#(Bit#(bus)) response;
            actionvalue
                let v <- inst.portA.response.get;
                return pack(v);
            endactionvalue
        endmethod
    endinterface);

    interface rw = rw_loc;

endmodule






module mkOpenRamBRAMDP#(BRAM2Port#(addr_t, data_t) inst) (OpenRAMIfc#(num_r, num_w, num_rw, addr_width, bus, 0)) provisos (
    Add#(num_r, num_w, a),
    Add#(a, num_rw, b), 
    Add#(b, _a, 2), // GF22 macros have two ports, do not exceed that

    Bits#(addr_t, addr_width),
    Bits#(data_t, bus)
);
    // track which port is currently mapped
    Integer current_port = 0;

    Vector#(num_r, RIfc#(addr_width, bus)) r_loc = ?;
    Vector#(num_w, WIfc#(addr_width, bus, 0)) w_loc = ?;
    Vector#(num_rw, RWIfc#(addr_width, bus, 0)) rw_loc = ?;

    // map ports to openSRAM iface
    for (Integer i= 0; i < valueOf(num_r); i=i+1) begin
        let p = current_port == 0 ? inst.portA: inst.portB;
        r_loc[i] = (interface RIfc;
            method Action request(Bit#(addr_width) addr);
                p.request.put(BRAMRequest {
                    address: unpack(addr),
                    write: False
                });
            endmethod
            method ActionValue#(Bit#(bus)) response;
                let v <- p.response.get;
                return pack(v);
            endmethod
        endinterface);
        current_port = current_port + 1;
    end

    for (Integer i= 0; i < valueOf(num_w); i=i+1) begin
        let p = current_port == 0 ? inst.portA: inst.portB;
        w_loc[i] = (interface WIfc;
            method Action request(Bit#(addr_width) addr, Bit#(bus) din, Bit#(0) mask);
                p.request.put(BRAMRequest {
                    address: unpack(addr),
                    write: True,
                    datain: unpack(din)
                });
            endmethod
        endinterface);
        current_port = current_port + 1;
    end

    for (Integer i= 0; i < valueOf(num_rw); i=i+1) begin
        let p = current_port == 0 ? inst.portA: inst.portB;
        rw_loc[0] = (interface RWIfc;
            method Action request(Bit#(addr_width) addr, Bit#(bus) din, Bit#(0) mask, Bool write_en);
                p.request.put(BRAMRequest {
                    address: unpack(addr),
                    write: write_en,
                    datain: unpack(din)
                });
            endmethod
            method ActionValue#(Bit#(bus)) response;
                actionvalue
                    let v <- p.response.get;
                    return pack(v);
                endactionvalue
            endmethod
        endinterface);
        current_port = current_port + 1;
    end

    interface r = r_loc;
    interface w = w_loc;
    interface rw = rw_loc;

endmodule


// same for the single-ported macro, this only supports 1 rw port since a read-only or write-only SRAM macro makes no sense
module mkOpenRamBRAMSP#(BRAM1Port#(addr_t, data_t) inst) (OpenRAMIfc#(0, 0, 1, addr_width, bus, 0)) provisos (
    Bits#(addr_t, addr_width),
    Bits#(data_t, bus)
);
    Vector#(num_rw, RWIfc#(addr_width, bus, 0)) rw_loc = ?;

    // map ports to openSRAM iface
    rw_loc[0] = (interface RWIfc;
        method Action request(Bit#(addr_width) addr, Bit#(bus) din, Bit#(0) mask, Bool write_en);
            inst.portA.request.put(BRAMRequest {
                address: unpack(addr),
                write: write_en,
                datain: unpack(din)
            });
        endmethod
        method ActionValue#(Bit#(bus)) response;
            actionvalue
                let v <- inst.portA.response.get;
                return pack(v);
            endactionvalue
        endmethod
    endinterface);

    interface rw = rw_loc;

endmodule

endpackage
