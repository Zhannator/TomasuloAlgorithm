# TomasuloAlgorithm
Tomasulo Algorithm implementation using Python

############################################################################################################
# CONFIGURATIONS SET FROM input_file.txt
############################################################################################################
# 1. # of ROB entries for each FU 
# 2. # of reservation stations for each FU
# 3. # of cycles for each FU
# 4. # of cycles for memory access 
# 5. ROB enties
# 6. set register values
# 7. set memory values
# 8. instructions
############################################################################################################

############################################################################################################
# INSTRUCTION SET ARCHITECTURE
############################################################################################################
# Data Transfer Instructions
# 	Ld Fa, offset(Ra)	Load a single precision floating point value to Fa
# 	Sd Fa, offset(Ra)	Store a single precision floating point value to memory
# Control Transfer Instructions
# 	Beq Rs, Rt, offset	If Rs==Rt then branch to PC+4+offset<<2
# 	Bne Rs, Rt, offset	If Rs!=Rt then branch to PC+4+offset<<2
# ALU Instructions
# 	Add Rd, Rs, Rt	Rd = Rs + Rt	Integer
# 	Add.d Fd, Fs, Ft	Fd = Fs + Ft	FP
# 	Addi Rt, Rs, immediate	Rt = Rs + immediate	Integer
# 	Sub Rd, Rs, Rt	Rd = Rs - Rt	Integer
# 	Sub.d Fd, Fs, Ft	Fd = Fs – Ft	FP
# 	Mult.d Fd, Fs, Ft	Fd = Fs * Ft, assuming that Fd is enough to hold the result	FP
############################################################################################################

############################################################################################################
# PIPELINE STAGES:
############################################################################################################
#  ISSUE: instruction fetch and decode, branch prediction
#     EX: calculates addresses for loads and stores, branch resolution, 
#		  uses load/store queue and doesn't occupy integer ALU, branch resolution
#    MEM: load can go to mem if no forwarding-from-a-store was found,
#		  takes 1 cycle to perform the forwarding if a match is found,
#         load gets the value and clears its entry in the queue
#     WB: broadcast results on CDB, write back to RS and ROB, mark ready bit in ROB
# COMMIT: when instruction is the oldest in ROB, store writes to memory (dequed)/write results to ARF,
#         advance ROB head to next instruction 
############################################################################################################

############################################################################################################
# PROCESSOR COMPONENTS:
############################################################################################################
# 1 instruction buffer: instruction_buffer
# 1 integer Architecture Register File (ARF): int_registers
# 1 floating point Architecture Register File (ARF): fp_registers
# 1 Register Aliasing Table (RAT): rat
# 1 Reservation Station (RS) for Adder: adder_rs
# 1 Reservation Station (RS) for Mult/Div: mult_div_rs
# 1 Common Data Bus (CDB)
# 1 Reorder Buffer (ROB): rob
# ? 1 Branch Predictor (BP)
# ? 1 Target Buffer (TB)
# 1 load/store queue (similar to reservation station for memory unit,
#	contains address and value (not useful for loads)): load_store_queue
############################################################################################################

############################################################################################################
# HARDWARE UNITS
############################################################################################################
# Integer adder; unpipelined
# FP adder; pipelined
# FP multiplier; pipelined
# Integer and FP register files, 32 entries each. Integer R0 is hardwired to 0.
# Memory; single-ported; non-pipelined
############################################################################################################

############################################################################################################
# BRANCH UNIT
############################################################################################################	
# Branch instructions are issued into the reservation stations of an integer ALU. We will 
# implement the simplest one-bit predictor for each branch instruction. Use a BTB of 8 entries to store 
# the target. Use the least significant 3 bits of the word address of the PC to index into the BTB. 
# Prediction is done in the first cycle of execution (ISSUE stage). The branch is resolved at the end of 
# the EX stage. Upon a misprediction, actions must be taken to squash wrong instructions. These include: 
# 1. recover the RAT; 2. clear the reservation station’s wait-for tag fields for wrong instructions; 
# 3. clear ROB entries that surpass the branch. Assume these actions take one cycle, and fetching from 
# the correct instruction starts in the next cycle. For example, if misprediction is detected in cycle n, 
# correct fetch should start at cycle n+2.
############################################################################################################
