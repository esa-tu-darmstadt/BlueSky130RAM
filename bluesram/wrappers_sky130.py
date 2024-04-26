from dataclasses import dataclass

@dataclass
class IfcDefinition:
    interface_implementation: str
    logic_implementation: str

# write preamble information to the lowlevel wrapper file
def write_port_interfaces(bsvFile, sram22, dffram):
    bsvFile.write(f"""
import {"SRAM22" if sram22 else "DFFRAM" if dffram else "OpenRAM"}_lowlevel_Wrappers::*;
import Vector::*;
import FIFO::*;
import SpecialFIFOs::*;
import OpenRAMIfc::*;

export OpenRAMIfc::*;
export {"SRAM22" if sram22 else "DFFRAM" if dffram else "OpenRAM"}Wrappers::*;

""")

# return the definition for an interface port of type RW
# macro_port refers to the port number in the macro
# type_port refers to the port number of this type
def create_rw_port(macro, macro_port_num, type_port_num, sram22, dffram):
    logic = f"""
    // handling of enable signals for macro
    Wire#(Bool) got_rq_{macro_port_num} <- mkDWire(False);
    // if no request is sent, we must send dummy values to statisfy always_enabled
    rule dummy_request{macro_port_num} if (!got_rq_{macro_port_num});
        {"// " if sram22 else ""}sram.rw{type_port_num}.ena({"True"}); // active low, disabled
        sram.rw{type_port_num}.request({"?" if not dffram else "0"}, ?, {"?, False" if not dffram else "pack(replicate(False))"}); // don't care, has no effect as ena is disabled
    endrule

    // adding guards for reading - only allow result method if result is available
    Wire#(Bool) got_rq_rd_{macro_port_num} <- mkDWire(False); // set if we got a read request in the current cycle
    Reg#(Bit#(1)) rd_shift_reg_{macro_port_num} <- mkReg(0); // shift register keeping track of when a response arrives
    rule advance_shift_{macro_port_num}; // advance shift register for result arrival tracking
        rd_shift_reg_{macro_port_num} <= {{truncate(rd_shift_reg_{macro_port_num}), pack(got_rq_rd_{macro_port_num})}};
    endrule

    // buffering of sram output if no guarding is enabled - necessary since signal values may be X if used unbuffered otherwise
    Reg#(Bit#({macro.data_width})) rs_buffering_{macro_port_num} <- mkRegU; // store result for one cycle
    Reg#(Bool) rs_buffering_valid_{macro_port_num} <- mkReg(False); // store if result was valid
    rule buffer_rs_{macro_port_num}; // populate the buffers
        rs_buffering_{macro_port_num} <= sram.rw{type_port_num}.response;
        rs_buffering_valid_{macro_port_num} <= unpack(truncateLSB(rd_shift_reg_{macro_port_num}));
    endrule
    
    // optional guarding of request method and buffering of responses
    Array#(Reg#(Bit#(2))) rd_rq_cnt_{macro_port_num} <- mkCReg(2, 0); // count in-flight requests
    FIFO#(Bit#({macro.data_width})) rs_buffer_fifo_{macro_port_num} <- mkSizedFIFO(3); // store not yet gathered responses
    // enqueue results into fifo until user requires them
    rule get_rs_into_fifo_{macro_port_num} if (truncateLSB(rd_shift_reg_{macro_port_num}) == 1'b1 && guard_rq_buffer_rs);
        rs_buffer_fifo_{macro_port_num}.enq(sram.rw{type_port_num}.response);
    endrule
    rule increment_request_counter_{macro_port_num} if (got_rq_rd_{macro_port_num});
        if (guard_rq_buffer_rs) rd_rq_cnt_{macro_port_num}[1] <= rd_rq_cnt_{macro_port_num}[1] + 1;
    endrule
    PulseWire deq_now_{macro_port_num} <- mkPulseWire();
    rule decrement_request_counter_{macro_port_num} if (deq_now_{macro_port_num});
        rd_rq_cnt_{macro_port_num}[0] <= rd_rq_cnt_{macro_port_num}[0] - 1;
    endrule

"""
    impl = f"""
    rw_loc[{type_port_num}] = (interface RWIfc;
        method Action request(Bit#({macro.addr_width}) addr, Bit#({macro.data_width}) din, Bit#({macro.wmask_width}) mask, Bool write_en)
            if (!guard_rq_buffer_rs || rd_rq_cnt_{macro_port_num}[0] < 3); // if guarded, stall when no further requests could be handled without loosing data
            got_rq_{macro_port_num} <= True; // stall dummy request logic
            // send request
            sram.rw{type_port_num}.request(addr, din, {"mask," if not dffram else "write_en ? mask : 0"} {"!" if not sram22 and not dffram else ""}{"write_en" if not dffram else ""});
            {"// " if sram22 else ""}sram.rw{type_port_num}.ena({"True" if dffram else "False"});
            if (!write_en) got_rq_rd_{macro_port_num} <= True; // notify shift register of read request
        endmethod
        method ActionValue#(Bit#({macro.data_width})) response 
            if (rs_buffering_valid_{macro_port_num} || guard_rq_buffer_rs); // stall if no result is available
            if (guard_rq_buffer_rs) begin
                // if guarded, get result from FIFO and decrease inflight requests
                deq_now_{macro_port_num}.send();
                rs_buffer_fifo_{macro_port_num}.deq();
                return rs_buffer_fifo_{macro_port_num}.first();
            end else
            // if unguarded use the register for result determination
            return rs_buffering_{macro_port_num};
        endmethod
    endinterface);

"""
    return IfcDefinition(interface_implementation=impl, logic_implementation=logic)


# return the definition for an interface port of type R
# macro_port refers to the port number in the macro
# type_port refers to the port number of this type
def create_r_port(macro, macro_port_num, type_port_num):
    logic = f"""
    // handling of enable signals for macro
    Wire#(Bool) got_rq_{macro_port_num} <- mkDWire(False);
    rule dummy_request{macro_port_num} if (!got_rq_{macro_port_num});
        sram.r{type_port_num}.ena(True); // active low, disabled
        sram.r{type_port_num}.request(?); // don't care, has no effect as ena is disabled
    endrule

    // adding guards for reading - only allow result method if result is available
    Reg#(Bit#(1)) rd_shift_reg_{macro_port_num} <- mkReg(0);
    rule advance_shift_{macro_port_num};
        rd_shift_reg_{macro_port_num} <= {{truncate(rd_shift_reg_{macro_port_num}), pack(got_rq_{macro_port_num})}};
    endrule

    // buffering of sram output if no guarding is enabled - necessary since signal values may be X if used unbuffered otherwise
    Reg#(Bit#({macro.data_width})) rs_buffering_{macro_port_num} <- mkRegU;
    Reg#(Bool) rs_buffering_valid_{macro_port_num} <- mkReg(False);
    rule buffer_rs_{macro_port_num};
        rs_buffering_{macro_port_num} <= sram.r{type_port_num}.response;
        rs_buffering_valid_{macro_port_num} <= unpack(truncateLSB(rd_shift_reg_{macro_port_num}));
    endrule
    
    // optional guarding of request method and buffering of responses
    Array#(Reg#(Bit#(2))) rd_rq_cnt_{macro_port_num} <- mkCReg(2, 0); // count in-flight requests
    FIFO#(Bit#({macro.data_width})) rs_buffer_fifo_{macro_port_num} <- mkSizedFIFO(3); // store not yet gathered responses
    // enqueue results into fifo until user requires them
    rule get_rs_into_fifo_{macro_port_num} if (truncateLSB(rd_shift_reg_{macro_port_num}) == 1'b1 && guard_rq_buffer_rs);
        rs_buffer_fifo_{macro_port_num}.enq(sram.r{type_port_num}.response);
    endrule
    rule increment_request_counter_{macro_port_num} if (got_rq_{macro_port_num});
        if (guard_rq_buffer_rs) rd_rq_cnt_{macro_port_num}[1] <= rd_rq_cnt_{macro_port_num}[1] + 1;
    endrule
    PulseWire deq_now_{macro_port_num} <- mkPulseWire();
    rule decrement_request_counter_{macro_port_num} if (deq_now_{macro_port_num});
        rd_rq_cnt_{macro_port_num}[0] <= rd_rq_cnt_{macro_port_num}[0] - 1;
    endrule
"""
    impl = f"""
    r_loc[{type_port_num}] = (interface RIfc;
        method Action request(Bit#({macro.addr_width}) addr) if (!guard_rq_buffer_rs || rd_rq_cnt_{macro_port_num}[0] < 3);
            got_rq_{macro_port_num} <= True;
            sram.r{type_port_num}.request(addr);
            sram.r{type_port_num}.ena(False);
        endmethod
        method ActionValue#(Bit#({macro.data_width})) response if (rs_buffering_valid_{macro_port_num} || guard_rq_buffer_rs);
            if (guard_rq_buffer_rs) begin
                deq_now_{macro_port_num}.send();
                rd_rq_cnt_{macro_port_num}[0] <= rd_rq_cnt_{macro_port_num}[0] - 1;
                rs_buffer_fifo_{macro_port_num}.deq();
                return rs_buffer_fifo_{macro_port_num}.first();
            end else
            return rs_buffering_{macro_port_num};
        endmethod
    endinterface);

"""
    return IfcDefinition(interface_implementation=impl, logic_implementation=logic)

# return the definition for an interface port of type W
# macro_port refers to the port number in the macro
# type_port refers to the port number of this type
def create_w_port(macro, macro_port_num, type_port_num):
    logic = f"""
    Wire#(Bool) got_rq_{macro_port_num} <- mkDWire(False);

    rule dummy_request{macro_port_num} if (!got_rq_{macro_port_num});
        sram.w{type_port_num}.ena(True); // active low, disabled
        sram.w{type_port_num}.request(?, ?, ?); // don't care, has no effect as ena is disabled
    endrule
"""
    impl = f"""
    w_loc[{type_port_num}] = (interface WIfc;
        method Action request(Bit#({macro.addr_width}) addr, Bit#({macro.data_width}) din, Bit#({macro.wmask_width}) mask);
            got_rq_{macro_port_num} <= True;
            sram.w{type_port_num}.request(addr, din, mask);
            sram.w{type_port_num}.ena(False);
        endmethod
    endinterface);

"""
    return IfcDefinition(interface_implementation=impl, logic_implementation=logic)

def create_wrapper(bsvFile, macro, sram22, dffram):
    if dffram:
        macro.data_width = "datawidth"
        macro.wmask_width = "databytes"

    interfaces = []
    # emit port information
    for n, p in enumerate(macro.ports_rw):
        interfaces.append(create_rw_port(macro, p, n, sram22, dffram))
    for n, p in enumerate(macro.ports_w):
        interfaces.append(create_w_port(macro, p, n))
    for n, p in enumerate(macro.ports_r):
        interfaces.append(create_r_port(macro, p, n))

    # produce lowlevel interface

    # write implementation
    datawidth = "datawidth" if dffram else macro.data_width
    databytes = "databytes" if dffram else macro.wmask_width
    params = ", Bool latches" if dffram else ""
    bsvFile.write(f"\nmodule mk_{macro.name}#(Bool guard_rq_buffer_rs{params}) (OpenRAMIfc#({len(macro.ports_r)}, {len(macro.ports_w)}, {len(macro.ports_rw)}, {macro.addr_width}, {datawidth}, {databytes}))")
    if dffram:
        bsvFile.write(" provisos(\n    Mul#(8, databytes, datawidth)\n)")
    bsvFile.write(";\n")

    params = "latches" if dffram else ""
    iface_name = "let" if not dffram else f"OR_{macro.name}_Ifc#(databytes)"
    bsvFile.write(f"    {iface_name} sram <- mk_{macro.name}_ll({params});\n")

    for i in interfaces:
        bsvFile.write(i.logic_implementation)

    bsvFile.write(f"    Vector#({len(macro.ports_r)}, RIfc#({macro.addr_width}, {macro.data_width})) r_loc = ?;\n")
    bsvFile.write(f"    Vector#({len(macro.ports_w)}, WIfc#({macro.addr_width}, {macro.data_width}, {macro.wmask_width})) w_loc = ?;\n")
    bsvFile.write(f"    Vector#({len(macro.ports_rw)}, RWIfc#({macro.addr_width}, {macro.data_width}, {macro.wmask_width})) rw_loc = ?;\n")

    for i in interfaces:
        bsvFile.write(i.interface_implementation)

    bsvFile.write(f"    interface r = r_loc;\n")
    bsvFile.write(f"    interface w = w_loc;\n")
    bsvFile.write(f"    interface rw = rw_loc;\n")

    bsvFile.write("endmodule\n\n\n")


def create_wrappers(macros, sram22, dffram):

    pkgname = "SRAM22Wrappers" if sram22 else "DFFRAMWrappers" if dffram else "OpenRAMWrappers"
    bsvFile = open(f"src/{pkgname}.bsv", "w")

    # header
    bsvFile.write(f"package {pkgname};\n")

    # write iface info
    write_port_interfaces(bsvFile, sram22, dffram)

    for macro in macros:
        create_wrapper(bsvFile, macro, sram22, dffram)
        
    # footer
    bsvFile.write(f"endpackage\n")