
def emit_typeclass_definition(bsvFile, ram_name):
    bsvFile.write(f"""

    typeclass {ram_name}#({"numeric type rd_ports, numeric type wr_ports, numeric type rw_ports, " if ram_name == "OpenRAM" else ""} numeric type addrwidth, numeric type datawidth, numeric type ena_width);
        module mk{ram_name}#(Bool backpressure)(OpenRAMIfc#({"rd_ports, wr_ports, rw_ports," if ram_name == "OpenRAM" else "0, 0, 1,"} addrwidth, datawidth, ena_width));
    endtypeclass

""")
    

def create_wrapper(bsvFile, macro, ram_name):

    typeclass_fragment = f"{len(macro.ports_r)}, {len(macro.ports_w)}, {len(macro.ports_rw)}, " if ram_name == "OpenRAM" else ""
    iface_fragment = f"{len(macro.ports_r)}, {len(macro.ports_w)}, {len(macro.ports_rw)}, " if ram_name == "OpenRAM" else "0, 0, 1, "

    bsvFile.write(f"""

    instance {ram_name}#({typeclass_fragment} {macro.addr_width}, {macro.data_width}, {macro.wmask_width});
        module mk{ram_name}#(Bool backpressure)(OpenRAMIfc#({iface_fragment} {macro.addr_width}, {macro.data_width}, {macro.wmask_width}));
            let inst <- mk_{macro.name}(backpressure);
            return asIfc(inst);
        endmodule
    endinstance

""")


def create_wrappers(macros, sram22):

    ram_name = "OpenRAM" if not sram22 else "SRAM22"

    bsvFile = open(f"src/{ram_name}.bsv", "w")

    # header
    bsvFile.write(f"package {ram_name};\n")

    bsvFile.write(f"import {ram_name}Wrappers::*;\n")

    # write iface info
    emit_typeclass_definition(bsvFile, ram_name)

    for macro in macros:
        create_wrapper(bsvFile, macro, ram_name)
        
    # footer
    bsvFile.write(f"endpackage\n")