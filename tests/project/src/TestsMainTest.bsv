package TestsMainTest;
    import StmtFSM :: *;
    import TestHelper :: *;
    import FIFO::*;
    import SpecialFIFOs::*;

    `ifdef OPENRAM
    import OpenRAMWrappers::*;
    import OpenRAM::*;
    import WrapBRAMAsOpenRAM::*;
    import BRAM::*;
    import Vector::*;

    `ifdef SRAM22
    import SRAM22_lowlevel_Wrappers::*;
    import SRAM22Wrappers::*;
    import SRAM22::*;
    `endif

    (* synthesize *)
    module [Module] mkTestsMainTest(TestHelper::TestHandler);

        //OpenRAMIfc#(0, 0, 1,  5, 9, 4) dut <- mkOpenRAM(True);

        `ifdef GUARDED
            Bool guard = True;
        `else
            Bool guard = False;
        `endif

        `ifdef BRAM
            BRAM_Configure cfg = defaultValue ; //declare variable cfg
            cfg.memorySize = 1024*32 ; //new value for memorySize
            BRAM2Port#(`ADDR_WIDTH, `DATA_WIDTH) bram <- mkBRAM2Server (cfg) ;
        `endif

        OpenRAMIfc#(`R_PORTS, `W_PORTS, `RW_PORTS, `ADDR_WIDTH, `DATA_WIDTH, `STROBES) dut
        `ifdef SRAM22
            <- mkSRAM22(guard)
        `endif
        `ifdef OPENRAM
            <- mkOpenRAM(guard)
        `endif
        `ifdef BRAM
            <- mkOpenRamBRAMDP(bram)
        `endif
        ;


        //SRAMServerBitEnDualPort#(8192, 128, 32, 8) t22 <- mkSRAMServerBitEnDualPort(True, False);
        //OpenRAMIfc#(0, 0, 1, 13, 32, 32) dut <- mkOpenRamGF22BitEnDP(t22);

        Reg#(UInt#(32)) ctr <- mkReg(0);
        Reg#(UInt#(32)) clk_ctr <- mkReg(0);

        rule init if (clk_ctr == 0);
            $display("Config:");
            $display("- Guarded: ", fshow(guard));
        endrule

        rule cnt_clk; clk_ctr <= clk_ctr +1; endrule

        rule cnt if (!((ctr >= 200 && ctr < 210))); ctr <= ctr + 1; endrule

        rule rq (ctr <= 'b1111);
            `ifdef TEST_W
                dut.w[0].request(pack(truncate(ctr)), pack(truncate(ctr)), truncate(32'hffffffff));
            `else
                dut.rw[0].request(pack(truncate(ctr)), pack(truncate(ctr)), truncate(32'hffffffff), True);
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
            let v <- dut.rw[0].response();
            results[ctr_res] <= v;
            ctr_res <= ctr_res + 1;
            $display("[%t] resp: ", $time, v);
        endrule

        rule end_sim (ctr == 1000);
            for (Integer i = 0; i <= 9; i=i+1) begin
                if(results[i] != fromInteger(i)) $display("FUCK");
            end
            $finish();
        endrule

    endmodule

endpackage
