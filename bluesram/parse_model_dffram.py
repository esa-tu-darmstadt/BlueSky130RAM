import os
import re
import sys
import math
from functools import reduce
import bluesram.wrappers_lowlevel_sky130 as ll_wrappers

def collect_macro_info(path):
    macros = []
    lines = open(path, "r").readlines()
    for l in lines:
        parts = l.split()
        if ("module" in l and len(parts) > 1):
            print("name: ", parts[1])
            name = parts[1]
            words = int(name.split("_")[0].replace("RAM", ""))
            addr_width = int(math.log2(words))

            macros.append(ll_wrappers.Macro(vlog=path, name=name, ports_r=([1] if "1RW1R" in name else []), ports_rw=[0], ports_w=[], data_width=0, addr_width=addr_width, wmask_width=0, tiehigh=[]))    
    return macros

if __name__ == "__main__":
    macros = collect_macro_info(sys.argv[1])
