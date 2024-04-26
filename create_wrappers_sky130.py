import argparse
import os
import re
import bluesram.wrappers_lowlevel_sky130 as ll_wrappers
import bluesram.wrappers_sky130 as hl_wrappers
import bluesram.typeclass_wrappers_sky130 as tc_wrappers
import bluesram.parse_model_dffram as dff_parser
from functools import reduce


def collect_macro_names(path, sram22):
    # get all subdirectories in openram output (also macro names)
    subdirs = [x for x in os.listdir(path) if os.path.isdir(os.path.join(path, x))]

    # return those collected macro names
    return subdirs


def collect_macro_info(path, names, sram22):
    macros = []

    for n in names:
        # get vlog file name
        vlog_file = os.path.join(path, n, n+".v")

        abs_vlog = os.path.abspath(vlog_file)
        # read simulation model - array of lines
        vlog_strings = open(vlog_file, "r").readlines()
        # extract necessary info

        # helper function to match regex onto a string
        def match_for_param(param, string):
            return re.search(f"\W*parameter\W*{param}\D*(\d+)", string)

        # remove mismatches from a list of potential matches
        def filter_mismatches(matches):
            return list(filter( lambda a: a != None, matches))

        # get integer value matched by regex
        def extract_match_value(match):
            return int(match[1])

        # match batch of strings
        def match_batch_for_param(param, strings):
            # match every line for parameter
            matches = filter_mismatches(map( lambda a: match_for_param(param, a), strings))
            # extract value
            # get first element of list - should only be one since the parameter is hopefully only set once
            # get first match
            if len(matches) == 0:
                return None
            else:
                return extract_match_value(matches[0])

        # helper functions to collect port types
        def match_port_r(string):
            # very important: RW contains R.... do not match RW as R
            return re.search(f"\W*Port (\d+): R([^W]|\Z)", string)

        def match_port_w(string):
            return re.search(f"\W*Port (\d+): W", string)

        def match_port_rw(string):
            return re.search(f"\W*Port (\d+): RW", string)

        # collect parameters
        data_width = match_batch_for_param("DATA_WIDTH", vlog_strings)
        addr_width = match_batch_for_param("ADDR_WIDTH", vlog_strings)
        wmask_width = None
        if not sram22:
            wmask_width = match_batch_for_param("NUM_WMASKS", vlog_strings)
        else:
            wmask_width = match_batch_for_param("WMASK_WIDTH", vlog_strings)
        if wmask_width is None:
            wmask_width = 0

        # match every line for port types and extract value
        # the lists contain the port number of a specific type
        ports_r = list(map(extract_match_value, filter_mismatches(map(match_port_r, vlog_strings))))
        ports_rw = list(map(extract_match_value, filter_mismatches(map(match_port_rw, vlog_strings))))
        ports_w = list(map(extract_match_value, filter_mismatches(map(match_port_w, vlog_strings))))

        # tiehigh signals
        tiehigh_num = 0
        tiehigh_ports = []
        if not sram22:
            tiehigh_num = map(extract_match_value, filter_mismatches([re.search("\W*input\W*spare_wen(\d+);[^\D]*", f) for f in vlog_strings]))
            tiehigh_ports = map(lambda a: "spare_wen"+str(a), tiehigh_num)
        else:
            ports_rw = [0]

        # generate final struct
        macros.append(ll_wrappers.Macro(vlog=abs_vlog, name=n, ports_r=ports_r, ports_rw=ports_rw, ports_w=ports_w, data_width=data_width, addr_width=addr_width, wmask_width=wmask_width, tiehigh=tiehigh_ports))

    return macros


if __name__ == "__main__":
    print("\033[48;2;0;0;255m\033[97m .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------. \033[0m")
    print("\033[48;2;0;0;255m\033[97m| .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |\033[0m")
    print("\033[48;2;0;0;255m\033[97m| |   ______     | || |   _____      | || | _____  _____ | || |  _________   | || |    _______   | || |  _______     | || |      __      | || | ____    ____ | |\033[0m")
    print("\033[48;2;0;0;255m\033[97m| |  |_   _ \    | || |  |_   _|     | || ||_   _||_   _|| || | |_   ___  |  | || |   /  ___  |  | || | |_   __ \    | || |     /  \     | || ||_   \  /   _|| |\033[0m")
    print("\033[48;2;0;0;255m\033[97m| |    | |_) |   | || |    | |       | || |  | |    | |  | || |   | |_  \_|  | || |  |  (__ \_|  | || |   | |__) |   | || |    / /\ \    | || |  |   \/   |  | |\033[0m")
    print("\033[48;2;0;0;255m\033[97m| |    |  __'.   | || |    | |   _   | || |  | '    ' |  | || |   |  _|  _   | || |   '.___`-.   | || |   |  __ /    | || |   / ____ \   | || |  | |\  /| |  | |\033[0m")
    print("\033[48;2;0;0;255m\033[97m| |   _| |__) |  | || |   _| |__/ |  | || |   \ `--' /   | || |  _| |___/ |  | || |  |`\____) |  | || |  _| |  \ \_  | || | _/ /    \ \_ | || | _| |_\/_| |_ | |\033[0m")
    print("\033[48;2;0;0;255m\033[97m| |  |_______/   | || |  |________|  | || |    `.__.'    | || | |_________|  | || |  |_______.'  | || | |____| |___| | || ||____|  |____|| || ||_____||_____|| |\033[0m")
    print("\033[48;2;0;0;255m\033[97m| |              | || |              | || |              | || |              | || |              | || |              | || |              | || |              | |\033[0m")
    print("\033[48;2;0;0;255m\033[97m| '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |\033[0m")
    print("\033[48;2;0;0;255m\033[97m '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------' \033[0m")

    parser = argparse.ArgumentParser()
    parser.add_argument("--sram22", action=argparse.BooleanOptionalAction, help="load SRAM22 macros instead of openRAM macros")
    parser.add_argument("--dffram", action=argparse.BooleanOptionalAction, help="load DFFRAM macros instead of openRAM macros")
    parser.add_argument("macro_dir", type=str, help="Folder containing the memory views")

    args = parser.parse_args()

    macros = None
    if not args.dffram:
        macros = collect_macro_info(args.macro_dir, collect_macro_names(args.macro_dir, args.sram22), args.sram22)
    else:
        macros = dff_parser.collect_macro_info(os.path.join(args.macro_dir, "model.v"))

    for macro in macros:
        print(macro)

    ll_wrappers.create_bvi_wrappers(macros, args.sram22, args.dffram)
    hl_wrappers.create_wrappers(macros, args.sram22, args.dffram)
    tc_wrappers.create_wrappers(macros, args.sram22, args.dffram)

    # write vlog sources to makefile
    # get vlog names
    dffram_files = ["model.v", "sky130.v", "block_definitions.v"]
    vlog_files = map(lambda a: a.vlog, macros) if not args.dffram else map(lambda a: os.path.abspath(os.path.join(args.macro_dir, a)), dffram_files)
    vlog_str = reduce(lambda a, b: a+" "+b, vlog_files)
    open("sram22.files" if args.sram22 else "dffram.files" if args.dffram else "openram.files", "w").write("C_FILES += " + vlog_str)
