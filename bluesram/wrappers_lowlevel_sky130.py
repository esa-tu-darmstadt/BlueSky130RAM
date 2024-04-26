from dataclasses import dataclass

@dataclass
class IfcDefinition:
    iface: str
    implementation: str
    schedules: list
    clock: str

@dataclass
class Macro:
    name: str
    ports_r: list
    ports_w: list
    ports_rw: list
    data_width: int
    addr_width: int
    wmask_width: int
    tiehigh: list
    vlog: str

# write preamble information to the lowlevel wrapper file
def write_preamble(bsvFile):
    bsvFile.write("""
import OpenRAMIfc::*; // import interfaces
              
""")

# return the definition for an interface port of type RW
# macro_port refers to the port number in the macro
# type_port refers to the port number of this type
def create_rw_port(macro, macro_port_num, type_port_num, sram22, dffram):
    macro_port_num_selection = macro_port_num if not sram22 else "0" if dffram else ""
    port_name_addr = "A" if dffram else "addr"
    port_name_din = "Di" if dffram else "din"
    port_name_wmask = "WE" if dffram else "wmask"
    port_name_ena = "EN" if dffram else "csb"
    port_name_dout = "Do" if dffram else "dout"
    port_name_clk = "CLK" if dffram else "clk"
    port_name_we = "web" if not sram22 else "we"

    write_ena_iface = f", {port_name_we}{macro_port_num_selection}" if not dffram else ""

    impl = f"""

    interface LL_RWIfc{"22" if sram22 else "DFF" if dffram else ""} rw{type_port_num};
        // since BSV only supports active-high, we do not use the enable signals but define our own
        method request ({port_name_addr}{macro_port_num_selection}, {port_name_din}{macro_port_num_selection}, {port_name_wmask}{macro_port_num_selection}{write_ena_iface}) enable((*inhigh*) placeholder_1_{macro_port_num}) clocked_by(dclk{macro_port_num});
        {f"method ena ({port_name_ena}{macro_port_num}) enable( (*inhigh*) placeholder_2_{macro_port_num}) clocked_by(dclk{macro_port_num});" if not sram22 else ""}
        method {port_name_dout}{macro_port_num_selection} response clocked_by(dclk{macro_port_num});
    endinterface
    input_clock ({port_name_clk}{"" if dffram else macro_port_num_selection}) = dclk{macro_port_num};

"""
    iface = f"""    interface LL_RWIfc{"22" if sram22 else "DFF" if dffram else ""}#({macro.addr_width}, {macro.data_width if not dffram else "TMul#(8, bytes)"}, {macro.wmask_width if not dffram else "bytes"}) rw{type_port_num};\n"""
    clock = f"    Clock dclk{macro_port_num} <- exposeCurrentClock;\n"

    schedule_fragment = f"rw{type_port_num}.ena, " if not sram22 else f""
    schedules = [
        f"    schedule ({schedule_fragment}rw{type_port_num}.response) CF (rw{type_port_num}.response, rw{type_port_num}.request);\n",     
        f"    schedule (rw{type_port_num}.request) C (rw{type_port_num}.request);\n",
        f"    schedule (rw{type_port_num}.ena) C (rw{type_port_num}.ena);\n" if not sram22 else ""
    ]
    return IfcDefinition(implementation=impl, iface=iface, schedules=schedules, clock=clock)


# return the definition for an interface port of type R
# macro_port refers to the port number in the macro
# type_port refers to the port number of this type
def create_r_port(macro, macro_port_num, type_port_num, dffram):

    port_name_addr = "A" if dffram else "addr"
    port_name_din = "Di" if dffram else "din"
    port_name_wmask = "WE" if dffram else "wmask"
    port_name_ena = "EN" if dffram else "csb"
    port_name_dout = "Do" if dffram else "dout"

    impl = f"""
    interface LL_RIfc r{type_port_num};
        // since BSV only supports active-high, we do not use the enable signals but define our own
        method request ({port_name_addr}{macro_port_num}) enable((*inhigh*) placeholder_1_{macro_port_num}) clocked_by(dclk{"0" if dffram else macro_port_num});
        method ena ({port_name_ena}{macro_port_num}) enable( (*inhigh*) placeholder_2_{macro_port_num}) clocked_by(dclk{"0" if dffram else macro_port_num});
        method {port_name_dout}{macro_port_num} response clocked_by(dclk{"0" if dffram else macro_port_num});
    endinterface

    {"// " if dffram else ""}input_clock (clk{macro_port_num}) = dclk{macro_port_num};

"""
    datawidth = macro.data_width if not dffram else "TMul#(8, bytes)"
    iface = f"    interface LL_RIfc#({macro.addr_width}, {datawidth}) r{type_port_num};\n"
    clock = f"    Clock dclk{macro_port_num} <- exposeCurrentClock;\n" if not dffram else ""
    schedules = [
        f"    schedule (r{type_port_num}.ena, r{type_port_num}.response) CF (r{type_port_num}.response, r{type_port_num}.request);\n",     
        f"    schedule (r{type_port_num}.request) C (r{type_port_num}.request);\n",
        f"    schedule (r{type_port_num}.ena) C (r{type_port_num}.ena);\n"
    ]
    return IfcDefinition(implementation=impl, iface=iface, schedules=schedules, clock=clock)

# return the definition for an interface port of type W
# macro_port refers to the port number in the macro
# type_port refers to the port number of this type
def create_w_port(macro, macro_port_num, type_port_num):
    impl = f"""
    interface LL_WIfc w{type_port_num};
        // since BSV only supports active-high, we do not use the enable signals but define our own
        method request (addr{macro_port_num}, din{macro_port_num}, wmask{macro_port_num}) enable((*inhigh*) placeholder_1_{macro_port_num}) clocked_by(dclk{macro_port_num});
        method ena (csb{macro_port_num}) enable( (*inhigh*) placeholder_2_{macro_port_num}) clocked_by(dclk{macro_port_num});
    endinterface

    input_clock (clk{macro_port_num}) = dclk{macro_port_num};

"""
    iface = f"    interface LL_WIfc#({macro.addr_width}, {macro.data_width}, {macro.wmask_width}) w{type_port_num};\n"
    clock = f"    Clock dclk{macro_port_num} <- exposeCurrentClock;\n"
    schedules = [
        f"    schedule (w{type_port_num}.ena) CF (w{type_port_num}.request);\n",     
        f"    schedule (w{type_port_num}.request) C (w{type_port_num}.request);\n",
        f"    schedule (w{type_port_num}.ena) C (w{type_port_num}.ena);\n"
    ]
    return IfcDefinition(implementation=impl, iface=iface, schedules=schedules, clock=clock)

def create_lowlevel_wrapper(bsvFile, macro, sram22, dffram):
    interfaces = []
    # emit port information
    for n, p in enumerate(macro.ports_rw):
        interfaces.append(create_rw_port(macro, p, n, sram22, dffram))
    for n, p in enumerate(macro.ports_w):
        interfaces.append(create_w_port(macro, p, n))
    for n, p in enumerate(macro.ports_r):
        interfaces.append(create_r_port(macro, p, n, dffram))

    # produce lowlevel interface
    params = "#(numeric type bytes)" if dffram else ""
    bsvFile.write(f"interface OR_{macro.name}_Ifc{params};\n")
    for i in interfaces:
        bsvFile.write(i.iface)
    bsvFile.write(f"endinterface\n\n")

    # write implementation
    parameter_string = "#(Bool latches)" if dffram else ""
    ifc_params = "#(bytes)" if dffram else ""
    bsvFile.write(f"import \"BVI\" {macro.name} = \nmodule mk_{macro.name}_ll{parameter_string} (OR_{macro.name}_Ifc{ifc_params});\n")

    for i in interfaces:
        bsvFile.write(i.clock)
        
    for i in interfaces:
        bsvFile.write(i.implementation)

    bsvFile.write("    default_clock no_clock;\n")
    bsvFile.write("    default_reset no_reset;\n\n")

    for i in interfaces:
        for t in macro.tiehigh:
            bsvFile.write(f"    port {t} = 1;\n")

    if (dffram):
        bsvFile.write(f"    parameter WSIZE = valueOf(bytes);\n")
        bsvFile.write(f"    parameter USE_LATCH = latches;\n")

    # write schedules
    for i in interfaces:
        for s in i.schedules:
            bsvFile.write(s)

    if dffram and len(macro.ports_r) > 0:
        bsvFile.write("    schedule (r0.response, r0.ena, r0.request) CF (rw0.request, rw0.ena, rw0.response);\n")

    bsvFile.write("endmodule\n\n\n")


def create_bvi_wrappers(macros, sram22, dffram):

    pkgname = "OpenRAM_lowlevel_Wrappers" if not sram22 and not dffram else "SRAM22_lowlevel_Wrappers" if sram22 else "DFFRAM_lowlevel_Wrappers"

    bsvFile = open(f"src/{pkgname}.bsv", "w")

    # header
    bsvFile.write(f"package {pkgname};\n")

    # write iface info
    write_preamble(bsvFile)

    for macro in macros:
        create_lowlevel_wrapper(bsvFile, macro, sram22, dffram)
        
    # footer
    bsvFile.write(f"endpackage\n")