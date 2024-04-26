
def emit_typeclass_definition(bsvFile, ram_name):

    rd_ports = "numeric type rd_ports, " if ram_name=="OpenRAM" or ram_name=="DFFRAM" else ""
    wr_ports = "numeric type wr_ports, " if ram_name=="OpenRAM" else ""
    rw_ports = "numeric type rw_ports, " if ram_name=="OpenRAM" else ""
    extra_params = ", Bool latches" if ram_name=="DFFRAM" else ""
    datawidth = "numeric type datawidth, " if not ram_name=="DFFRAM" else ""

    rd_value = "rd_ports" if ram_name != "SRAM22" else "0"
    wr_value = "wr_ports" if ram_name == "OpenRAM" else "0"
    rw_value = "rw_ports" if ram_name == "OpenRAM" else "1"
    width_value = "datawidth" if not ram_name == "DFFRAM" else "TMul#(8, ena_width)"

    bsvFile.write(f"""

    typeclass {ram_name}#({rd_ports}{wr_ports}{rw_ports}numeric type addrwidth, {datawidth}numeric type ena_width);
        module mk{ram_name}#(Bool backpressure{extra_params})(OpenRAMIfc#({rd_value}, {wr_value}, {rw_value}, addrwidth, {width_value}, ena_width));
    endtypeclass

""")
    

def create_wrapper(bsvFile, macro, ram_name):

    typeclass_fragment = f"{len(macro.ports_r)}, {len(macro.ports_w)}, {len(macro.ports_rw)}, " if ram_name == "OpenRAM" else f"{len(macro.ports_r)}, " if ram_name == "DFFRAM" else ""
    iface_fragment = f"{len(macro.ports_r)}, {len(macro.ports_w)}, {len(macro.ports_rw)}, " if ram_name != "SRAM22" else "0, 0, 1, "
    datawidth_fragment = f"{macro.data_width}, " if not ram_name=="DFFRAM" else ""


    bsvFile.write(f"""

    instance {ram_name}#({typeclass_fragment}{macro.addr_width}, {datawidth_fragment}{macro.wmask_width});
        module mk{ram_name}#(Bool backpressure{", Bool latches" if ram_name=="DFFRAM" else ""})(OpenRAMIfc#({iface_fragment} {macro.addr_width}, {macro.data_width if not ram_name=="DFFRAM" else "TMul#(8, databytes)"}, {macro.wmask_width}));
            let inst <- mk_{macro.name}(backpressure{", latches" if ram_name=="DFFRAM" else ""});
            return asIfc(inst);
        endmodule
    endinstance

""")


def create_wrappers(macros, sram22, dffram):

    ram_name = "SRAM22" if sram22 else "DFFRAM" if dffram else "OpenRAM"

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