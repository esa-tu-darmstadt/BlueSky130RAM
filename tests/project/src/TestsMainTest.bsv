package TestsMainTest;
    import StmtFSM :: *;
    import TestHelper :: *;
    import FIFO::*;
    import SpecialFIFOs::*;
    import OpenRAMIfc::*;

    `ifdef OPENRAM
    import OpenRAMWrappers::*;
    import OpenRAM::*;
    `endif
    
    import WrapBRAMAsOpenRAM::*;
    import BRAM::*;
    import Vector::*;

    `ifdef SRAM22
    import SRAM22_lowlevel_Wrappers::*;
    import SRAM22Wrappers::*;
    import SRAM22::*;
    `endif

    `ifdef DFFRAM
    import DFFRAM::*;
    `endif

    import Assertions :: *;
    import BUtils::*;

    (* synthesize *)
    module [Module] mkTestsMainTest(Empty);

        `ifdef GUARDED
            Bool guard = True;
        `else
            Bool guard = False;
        `endif

        `ifdef BRAMDP
            BRAM_Configure cfg = defaultValue ; //declare variable cfg
            cfg.memorySize = 32 ; //new value for memorySize
            BRAM2Port#(Bit#(`ADDR_WIDTH), Bit#(`DATA_WIDTH)) bram <- mkBRAM2Server (cfg);
        `endif

        `ifdef BRAMSP
            BRAM_Configure cfg = defaultValue ; //declare variable cfg
            cfg.memorySize = 32 ; //new value for memorySize
            BRAM1Port#(Bit#(`ADDR_WIDTH), Bit#(`DATA_WIDTH)) bram <- mkBRAM1Server (cfg);
        `endif

        `ifdef BRAMDPBE
            BRAM_Configure cfg = defaultValue ; //declare variable cfg
            cfg.memorySize = 32 ; //new value for memorySize
            BRAM2PortBE#(Bit#(`ADDR_WIDTH), Bit#(`DATA_WIDTH), 4) bram <- mkBRAM2ServerBE (cfg);
        `endif

        `ifdef BRAMSPBE
            BRAM_Configure cfg = defaultValue ; //declare variable cfg
            cfg.memorySize = 32 ; //new value for memorySize
            BRAM1PortBE#(Bit#(`ADDR_WIDTH), Bit#(`DATA_WIDTH), 4) bram <- mkBRAM1ServerBE (cfg);
        `endif

        OpenRAMIfc#(`R_PORTS, `W_PORTS, `RW_PORTS, `ADDR_WIDTH, `DATA_WIDTH, `STROBES) dut
        `ifdef SRAM22
            <- mkSRAM22(guard)
        `endif
        `ifdef OPENRAM
            <- mkOpenRAM(guard)
        `endif
        `ifdef BRAMDP
            <- mkOpenRamBRAMDP(bram)
        `endif
        `ifdef BRAMSP
            <- mkOpenRamBRAMSP(bram)
        `endif
        `ifdef BRAMDPBE
            <- mkOpenRamBRAMByteEnDP(bram)
        `endif
        `ifdef BRAMSPBE
            <- mkOpenRamBRAMByteEnSP(bram)
        `endif
        `ifdef DFFRAM
            <- mkDFFRAM(guard, unpack(`LATCHED))
        `endif
        ;




        Reg#(UInt#(32)) ctr <- mkReg(0);
        Reg#(UInt#(32)) clk_ctr <- mkReg(0);

        rule init if (clk_ctr == 0);
            $display("Config:");
            $display("- Guarded: ", fshow(guard));
        endrule

        rule cnt_clk; clk_ctr <= clk_ctr +1; endrule

        rule cnt if (!((ctr >= 200 && ctr < 210))); ctr <= ctr + 1; endrule

        rule rq (ctr <= 10 && ctr > 0);
            `ifdef TEST_W
                dut.w[0].request(pack(truncate(ctr-1)), cExtend(pack(ctr-1)), pack(replicate(1'b1)));
            `else
                dut.rw[0].request(pack(truncate(ctr-1)), cExtend(pack(ctr-1)), pack(replicate(1'b1)), True);
            `endif
        endrule

        rule rq_rd (ctr >= 200 && ctr < 210);
            `ifdef TEST_R
                dut.r[0].request(pack(truncate(ctr - 200)));
            `else
                dut.rw[0].request(pack(truncate(ctr - 200)), 0, 0, False);
            `endif
            ctr <= ctr + 1;
        endrule

        FIFO#(Bit#(8)) val_w <- mkPipelineFIFO();

        Reg#(Vector#(10, Bit#(32))) results <- mkRegU;
        Reg#(UInt#(8)) ctr_res <- mkReg(0);

        rule rq_rs if (clk_ctr > 500 || !guard);
            let v <- 
            `ifdef TEST_R
                dut.r[0].response();
            `else
                dut.rw[0].response();
            `endif
            if (ctr_res <= 9) results[ctr_res] <= cExtend(v);
            ctr_res <= ctr_res + 1;
            $display("[%t] resp: ", $time, v);
        endrule

        rule end_sim (ctr == 1000);
            for (Integer i = 0; i <= 9; i=i+1) begin
                let err_msg = $format("A read value was wrong");
                assertEquals(results[i], fromInteger(i), err_msg);
            end
            $finish();
        endrule

    endmodule

endpackage
