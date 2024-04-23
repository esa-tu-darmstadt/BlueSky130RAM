// SRAM22 SRAM model
// Words: 64
// Word size: 32
// Write size: 4

module sram22_64x32m4w4(
`ifdef USE_POWER_PINS
    vdd,
    vss,
`endif
  clk,we,wmask,addr,din,dout
  );

  // These parameters should NOT be set to
  // anything other than their defaults.
  parameter DATA_WIDTH = 32 ;
  parameter ADDR_WIDTH = 6 ;
  parameter WMASK_WIDTH = 8 ;
  parameter RAM_DEPTH = 1 << ADDR_WIDTH;

`ifdef USE_POWER_PINS
    inout vdd; // power
    inout vss; // ground
`endif
  input  clk; // clock
  input  we; // write enable
  input [WMASK_WIDTH-1:0] wmask; // write mask
  input [ADDR_WIDTH-1:0]  addr; // address
  input [DATA_WIDTH-1:0]  din; // data in
  output reg [DATA_WIDTH-1:0] dout; // data out
  

  reg [DATA_WIDTH-1:0] mem [0:RAM_DEPTH-1];

  // Fill memory with zeros.
  // For simulation only. The real SRAM
  // may not be initialized to all zeros.
  integer i;
  initial begin
    for (i = 0 ; i < RAM_DEPTH ; i = i + 1)
    begin
      mem[i] = {DATA_WIDTH{1'b0}};
    end
  end

  always @(posedge clk)
  begin
    // Write
    if (we) begin
        if (wmask[0]) begin
          mem[addr][3:0] <= din[3:0];
        end
        if (wmask[1]) begin
          mem[addr][7:4] <= din[7:4];
        end
        if (wmask[2]) begin
          mem[addr][11:8] <= din[11:8];
        end
        if (wmask[3]) begin
          mem[addr][15:12] <= din[15:12];
        end
        if (wmask[4]) begin
          mem[addr][19:16] <= din[19:16];
        end
        if (wmask[5]) begin
          mem[addr][23:20] <= din[23:20];
        end
        if (wmask[6]) begin
          mem[addr][27:24] <= din[27:24];
        end
        if (wmask[7]) begin
          mem[addr][31:28] <= din[31:28];
        end

      // Output is arbitrary when writing to SRAM
      dout <= {DATA_WIDTH{1'bx}};
    end

    // Read
    if (!we) begin
      dout <= mem[addr];
    end
  end

endmodule

