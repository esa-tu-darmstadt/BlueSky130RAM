package EFSRAM;

import OpenRAMIfc::*; // import interfaces
import FIFO::*;
import SpecialFIFOs::*;
import Vector::*;

module mkEFSRAM#(Bool guard_rq_buffer_rs) (OpenRAMIfc#(0, 0, 1, 10, 32, 4));

    // internal
    let ll <- mk_EFSRAM_ll;

    // handling of enable signals for macro
    Wire#(Bool) got_rq_0 <- mkDWire(False);
    // if no request is sent, we must send dummy values to statisfy always_enabled
    rule dummy_request0 if (!got_rq_0);
        ll.rw0.ena(False); // active low, disabled
        ll.rw0.request(0, 0, 0, False); // don't care, has no effect as ena is disabled
    endrule

    // adding guards for reading - only allow result method if result is available
    Wire#(Bool) got_rq_rd_0 <- mkDWire(False); // set if we got a read request in the current cycle
    Reg#(Bit#(1)) rd_shift_reg_0 <- mkReg(0); // shift register keeping track of when a response arrives
    rule advance_shift_0; // advance shift register for result arrival tracking
        rd_shift_reg_0 <= {truncate(rd_shift_reg_0), pack(got_rq_rd_0)};
    endrule
    
    // optional guarding of request method and buffering of responses
    Array#(Reg#(Bit#(2))) rd_rq_cnt_0 <- mkCReg(2, 0); // count in-flight requests
    FIFO#(Bit#(32)) rs_buffer_fifo_0 <- mkSizedFIFO(3); // store not yet gathered responses
    // enqueue results into fifo until user requires them
    rule get_rs_into_fifo_0 if (truncateLSB(rd_shift_reg_0) == 1'b1 && guard_rq_buffer_rs);
        rs_buffer_fifo_0.enq(ll.rw0.response);
    endrule
    rule increment_request_counter_0 if (got_rq_rd_0);
        if (guard_rq_buffer_rs) rd_rq_cnt_0[1] <= rd_rq_cnt_0[1] + 1;
    endrule
    PulseWire deq_now_0 <- mkPulseWire();
    rule decrement_request_counter_0 if (deq_now_0);
        rd_rq_cnt_0[0] <= rd_rq_cnt_0[0] - 1;
    endrule

    Vector#(1, RWIfc#(10, 32, 4)) rw_loc = ?;

    rw_loc[0] = (interface RWIfc;
        method Action request(Bit#(10) addr, Bit#(32) din, Bit#(4) mask, Bool write_en)
            if (!guard_rq_buffer_rs || rd_rq_cnt_0[0] < 3); // if guarded, stall when no further requests could be handled without loosing data
            got_rq_0 <= True; // stall dummy request logic
            // send request
            Vector#(4, Bit#(1)) mask_  = unpack(mask);
            Vector#(4, Bit#(8)) mask_b = map(compose(pack, replicate), mask_);
            ll.rw0.request(addr, din, pack(mask_b), !write_en);
            ll.rw0.ena(True);
            if (!write_en) got_rq_rd_0 <= True; // notify shift register of read request

            $display("REQ: ", fshow(addr), " ", fshow(din), " ", fshow(mask), " ", fshow(write_en));
        endmethod
        method ActionValue#(Bit#(32)) response 
            if (unpack(truncateLSB(rd_shift_reg_0)) || guard_rq_buffer_rs); // stall if no result is available
            if (guard_rq_buffer_rs) begin
                // if guarded, get result from FIFO and decrease inflight requests
                deq_now_0.send();
                rs_buffer_fifo_0.deq();
                return rs_buffer_fifo_0.first();
            end else
            // if unguarded use the register for result determination
            return ll.rw0.response;
        endmethod
    endinterface);

    interface rw = rw_loc;

endmodule

interface EFSRAMLLIfc;
    interface LL_RWIfc#(10, 32, 32) rw0;
endinterface

import "BVI" EF_SRAM_1024x32 = 
module mk_EFSRAM_ll (EFSRAMLLIfc);
    Clock dclk0 <- exposeCurrentClock;


    interface LL_RWIfc rw0;
        // since BSV only supports active-high, we do not use the enable signals but define our own
        method request (AD, DI, BEN, R_WB) enable((*inhigh*) placeholder_1_0) clocked_by(dclk0);
        method ena (EN) enable( (*inhigh*) placeholder_2_0) clocked_by(dclk0);
        method DO response clocked_by(dclk0);
    endinterface

    input_clock (CLKin) = dclk0;

    // tie off pins
    port vpwrac = 1'b1;
    port vpwrpc = 1'b1;

    port TM = 'b0;
    port SM = 'b0;
    port ScanInCC = 'b0;
    port ScanInDL = 'b0;
    port ScanInDR = 'b0;
    port WLBI = 'b0;
    port WLOFF = 'b0;

    default_clock no_clock;
    default_reset no_reset;

    schedule (rw0.ena, rw0.response) CF (rw0.response, rw0.request);
    schedule (rw0.request) C (rw0.request);
    schedule (rw0.ena) C (rw0.ena);
endmodule


endpackage