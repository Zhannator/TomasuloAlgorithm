# TomasuloAlgorithm
Tomasulo Algorithm implementation using Python

#################################################################################
CONFIGURATIONS SET FROM input_file.txt
#################################################################################
number of ROB entries, number of reservation stations for each function unit, number of cycles for EX stage for each function unit, number of cycles for memory access, number of ROB enties, register values, memory values, instructions

#################################################################################
INSTRUCTION SET ARCHITECTURE
#################################################################################
Data Transfer Instructions
    Ld Fa, offset(Ra)	Load a single precision floating point value to Fa
    Sd Fa, offset(Ra)	Store a single precision floating point value to memory
Control Transfer Instructions
    Beq Rs, Rt, offset	If Rs==Rt then branch to PC+4+offset<<2
    Bne Rs, Rt, offset	If Rs!=Rt then branch to PC+4+offset<<2
ALU Instructions
    Add Rd, Rs, Rt	Rd = Rs + Rt	Integer
    Add.d Fd, Fs, Ft	Fd = Fs + Ft	FP
    Addi Rt, Rs, immediate	Rt = Rs + immediate	Integer
    Sub Rd, Rs, Rt	Rd = Rs - Rt	Integer
    Sub.d Fd, Fs, Ft	Fd = Fs – Ft	FP
    Mult.d Fd, Fs, Ft	Fd = Fs * Ft, assume Fd is enough to hold the result FP

#################################################################################
PIPELINE STAGES:
#################################################################################
ISSUE, EX, MEM, WB, COMMIT

#################################################################################
PROCESSOR COMPONENTS:
#################################################################################
1 instruction buffer: instruction_buffer
1 integer Architecture Register File (ARF): int_registers
1 floating point Architecture Register File (ARF): fp_registers
1 Register Aliasing Table (RAT): rat
1 Reservation Station (RS) for Adder: adder_rs
1 Reservation Station (RS) for Mult/Div: mult_div_rs
1 Common Data Bus (CDB)
1 Reorder Buffer (ROB): rob
1 load/store queue (similar to reservation station for memory unit,
  contains address and value (not useful for loads)): load_store_queue

#################################################################################
HARDWARE UNITS
#################################################################################
Integer adder; unpipelined
FP adder; pipelined
FP multiplier; pipelined
Integer and FP register files, 32 entries each. Integer R0 is hardwired to 0.
Memory; single-ported; non-pipelined