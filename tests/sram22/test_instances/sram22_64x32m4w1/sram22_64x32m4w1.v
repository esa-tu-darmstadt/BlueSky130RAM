// SRAM22 SRAM model
// Words: 64
// Word size: 32
// Write size: 1

module sram22_64x32m4w1(
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
  parameter WMASK_WIDTH = 32 ;
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
          mem[addr][0:0] <= din[0:0];
        end
        if (wmask[1]) begin
          mem[addr][1:1] <= din[1:1];
        end
        if (wmask[2]) begin
          mem[addr][2:2] <= din[2:2];
        end
        if (wmask[3]) begin
          mem[addr][3:3] <= din[3:3];
        end
        if (wmask[4]) begin
          mem[addr][4:4] <= din[4:4];
        end
        if (wmask[5]) begin
          mem[addr][5:5] <= din[5:5];
        end
        if (wmask[6]) begin
          mem[addr][6:6] <= din[6:6];
        end
        if (wmask[7]) begin
          mem[addr][7:7] <= din[7:7];
        end
        if (wmask[8]) begin
          mem[addr][8:8] <= din[8:8];
        end
        if (wmask[9]) begin
          mem[addr][9:9] <= din[9:9];
        end
        if (wmask[10]) begin
          mem[addr][10:10] <= din[10:10];
        end
        if (wmask[11]) begin
          mem[addr][11:11] <= din[11:11];
        end
        if (wmask[12]) begin
          mem[addr][12:12] <= din[12:12];
        end
        if (wmask[13]) begin
          mem[addr][13:13] <= din[13:13];
        end
        if (wmask[14]) begin
          mem[addr][14:14] <= din[14:14];
        end
        if (wmask[15]) begin
          mem[addr][15:15] <= din[15:15];
        end
        if (wmask[16]) begin
          mem[addr][16:16] <= din[16:16];
        end
        if (wmask[17]) begin
          mem[addr][17:17] <= din[17:17];
        end
        if (wmask[18]) begin
          mem[addr][18:18] <= din[18:18];
        end
        if (wmask[19]) begin
          mem[addr][19:19] <= din[19:19];
        end
        if (wmask[20]) begin
          mem[addr][20:20] <= din[20:20];
        end
        if (wmask[21]) begin
          mem[addr][21:21] <= din[21:21];
        end
        if (wmask[22]) begin
          mem[addr][22:22] <= din[22:22];
        end
        if (wmask[23]) begin
          mem[addr][23:23] <= din[23:23];
        end
        if (wmask[24]) begin
          mem[addr][24:24] <= din[24:24];
        end
        if (wmask[25]) begin
          mem[addr][25:25] <= din[25:25];
        end
        if (wmask[26]) begin
          mem[addr][26:26] <= din[26:26];
        end
        if (wmask[27]) begin
          mem[addr][27:27] <= din[27:27];
        end
        if (wmask[28]) begin
          mem[addr][28:28] <= din[28:28];
        end
        if (wmask[29]) begin
          mem[addr][29:29] <= din[29:29];
        end
        if (wmask[30]) begin
          mem[addr][30:30] <= din[30:30];
        end
        if (wmask[31]) begin
          mem[addr][31:31] <= din[31:31];
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

