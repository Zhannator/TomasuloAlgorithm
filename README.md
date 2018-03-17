# TomasuloAlgorithm\n
Tomasulo Algorithm implementation using Python\n
\n
######################################\n
CONFIGURATIONS SET FROM input_file.txt\n
######################################\n
number of ROB entries, number of reservation stations for each function unit, \n
number of cycles for EX stage for each function unit, number of cycles for memory access, \n
number of ROB enties, register values, memory values, instructions\n
\n
######################################\n
INSTRUCTION SET ARCHITECTURE\n
######################################\n
Data Transfer Instructions\n
    Ld Fa, offset(Ra)	Load a single precision floating point value to Fa\n
    Sd Fa, offset(Ra)	Store a single precision floating point value to memory\n
Control Transfer Instructions\n
    Beq Rs, Rt, offset	If Rs==Rt then branch to PC+4+offset<<2\n
    Bne Rs, Rt, offset	If Rs!=Rt then branch to PC+4+offset<<2\n
ALU Instructions\n
    Add Rd, Rs, Rt	Rd = Rs + Rt	Integer\n
    Add.d Fd, Fs, Ft	Fd = Fs + Ft	FP\n
    Addi Rt, Rs, immediate	Rt = Rs + immediate	Integer\n
    Sub Rd, Rs, Rt	Rd = Rs - Rt	Integer\n
    Sub.d Fd, Fs, Ft	Fd = Fs – Ft	FP\n
    Mult.d Fd, Fs, Ft	Fd = Fs * Ft, assume Fd is enough to hold the result FP\n
\n
######################################\n
PIPELINE STAGES:\n
######################################\n
ISSUE, EX, MEM, WB, COMMIT\n
\n
######################################\n
PROCESSOR COMPONENTS:\n
######################################\n
1 instruction buffer: instruction_buffer\n
1 integer Architecture Register File (ARF): int_registers\n
1 floating point Architecture Register File (ARF): fp_registers\n
1 Register Aliasing Table (RAT): rat\n
1 Reservation Station (RS) for Adder: adder_rs\n
1 Reservation Station (RS) for Mult/Div: mult_div_rs\n
1 Common Data Bus (CDB)\n
1 Reorder Buffer (ROB): rob\n
1 load/store queue (similar to reservation station for memory unit,\n
  contains address and value (not useful for loads)): load_store_queue\n
\n
######################################\n
HARDWARE UNITS\n
######################################\n
Integer adder; unpipelined\n
FP adder; pipelined\n
FP multiplier; pipelined\n
Integer and FP register files, 32 entries each. Integer R0 is hardwired to 0.\n
Memory; single-ported; non-pipelined\n
