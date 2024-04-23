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
def create_rw_port(macro, macro_port_num, type_port_num, sram22):
    macro_port_num_selection = macro_port_num if not sram22 else ""
    
    impl = f"""

    interface LL_RWIfc{"22" if sram22 else ""} rw{type_port_num};
        // since BSV only supports active-high, we do not use the enable signals but define our own
        method request (addr{macro_port_num_selection}, din{macro_port_num_selection}, wmask{macro_port_num_selection}, {"web"  if not sram22 else "we"}{macro_port_num_selection}) enable((*inhigh*) placeholder_1_{macro_port_num}) clocked_by(dclk{macro_port_num});
        {f"method ena (csb{macro_port_num}) enable( (*inhigh*) placeholder_2_{macro_port_num}) clocked_by(dclk{macro_port_num});" if not sram22 else ""}
        method dout{macro_port_num_selection} response clocked_by(dclk{macro_port_num});
    endinterface
    input_clock (clk{macro_port_num_selection}) = dclk{macro_port_num};

"""
    iface = f"""    interface LL_RWIfc{"22" if sram22 else ""}#({macro.addr_width}, {macro.data_width}, {macro.wmask_width}) rw{type_port_num};\n"""
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
def create_r_port(macro, macro_port_num, type_port_num):
    impl = f"""
    interface LL_RIfc r{type_port_num};
        // since BSV only supports active-high, we do not use the enable signals but define our own
        method request (addr{macro_port_num}) enable((*inhigh*) placeholder_1_{macro_port_num}) clocked_by(dclk{macro_port_num});
        method ena (csb{macro_port_num}) enable( (*inhigh*) placeholder_2_{macro_port_num}) clocked_by(dclk{macro_port_num});
        method dout{macro_port_num} response clocked_by(dclk{macro_port_num});
    endinterface

    input_clock (clk{macro_port_num}) = dclk{macro_port_num};

"""
    iface = f"    interface LL_RIfc#({macro.addr_width}, {macro.data_width}) r{type_port_num};\n"
    clock = f"    Clock dclk{macro_port_num} <- exposeCurrentClock;\n"
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

def create_lowlevel_wrapper(bsvFile, macro, sram22):
    interfaces = []
    # emit port information
    for n, p in enumerate(macro.ports_rw):
        interfaces.append(create_rw_port(macro, p, n, sram22))
    for n, p in enumerate(macro.ports_w):
        interfaces.append(create_w_port(macro, p, n))
    for n, p in enumerate(macro.ports_r):
        interfaces.append(create_r_port(macro, p, n))

    # produce lowlevel interface
    bsvFile.write(f"interface OR_{macro.name}_Ifc;\n")
    for i in interfaces:
        bsvFile.write(i.iface)
    bsvFile.write(f"endinterface\n\n")

    # write implementation
    bsvFile.write(f"import \"BVI\" {macro.name} = \nmodule mk_{macro.name}_ll (OR_{macro.name}_Ifc);\n")

    for i in interfaces:
        bsvFile.write(i.clock)
        
    for i in interfaces:
        bsvFile.write(i.implementation)

    bsvFile.write("    default_clock no_clock;\n")
    bsvFile.write("    default_reset no_reset;\n\n")

    for i in interfaces:
        for t in macro.tiehigh:
            bsvFile.write(f"    port {t} = 1;\n")

    # write schedules
    for i in interfaces:
        for s in i.schedules:
            bsvFile.write(s)

    bsvFile.write("endmodule\n\n\n")


def create_bvi_wrappers(macros, sram22):

    bsvFile = open("src/OpenRAM_lowlevel_Wrappers.bsv" if not sram22 else "src/SRAM22_lowlevel_Wrappers.bsv", "w")

    # header
    bsvFile.write(f"package OpenRAM_lowlevel_Wrappers;\n" if not sram22 else f"package SRAM22_lowlevel_Wrappers;\n")

    # write iface info
    write_preamble(bsvFile)

    for macro in macros:
        create_lowlevel_wrapper(bsvFile, macro, sram22)
        
    # footer
    bsvFile.write(f"endpackage\n")