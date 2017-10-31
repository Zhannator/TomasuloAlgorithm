#!/usr/bin/python
# -*- coding: utf-8 -*-

############################################################################################################
# HOW TO RUN tomasulo_main
############################################################################################################
# tomasulo_main.py 
# 1. # of ROB entries 
# 2. # of reservation stations for each FU
# 3. # of cycles for each FU
# 4. # of cycles for memory access 
# 5. #
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
# 1 instruction buffer
# 1 integer Architecture Register File (ARF)
# 1 floating point Architecture Register File (ARF)
# 1 Register Aliasing Table (RAT)
# 1 Reservation Station (RS) for Adder
# 1 Reservation Station (RS) for Mult/Div
# 1 Common Data Bus (CDB)
# 1 Reorder Buffer (ROB)
# 1 Branch Predictor (BP)
# 1 Target Buffer (TB)
# 1 load/store queue (similar to reservation station for memory unit,
#	contains address and value (not useful for loads))
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

import sys

# Global Variables
memory = [] # needs to be initialized, 256B(64W), needs its own function on how to reference locations in mem by word/byte

############################################################################################################
# MAIN
############################################################################################################		
#def main(argv): # argv is a list of command line arguments
def main():
	# command line arguments
	# write later
	
	# assume for now everything takes one cycle
	# assume no dependencies
	
    cycle_counter = 0;
    instruction_counter = 0;
    pipeline = [-1, -1, -1, -1, -1] # 5 stages: ISSUE(0), EX(1), MEM(2), WB(3), and COMMIT(4)
    PC = 0 # in words
    instructions = ["Add.d R1, R2, R3", "Add.d R1, R2, R3", "Add.d R1, R2, R3", "Add.d R1, R2, R3", "Add.d R1, R2, R3"]
	
    for instruction in instructions:
        #leaving_instruction = pipeline[4]
        for i in range(4, 0, -1): # 5 stages
            pipeline[i] = pipeline[i-1] # need to accomodate for leaving instructions
        # get new instruction
        pipeline[0] = PC;
        PC = PC + 4;
        cycle_counter = cycle_counter + 1;
        # advance instructions in pipeline
        print ("Current cycle: " + str(cycle_counter))
        print ("Current state: " + str(pipeline))
    # advance leftover instructions in pipeline
    for j in range(0, 5):
        #leaving_instruction = pipeline[4]
        for i in range(4, 0, -1): # 5 stages
            pipeline[i] = pipeline [i-1] # need to accomodate for leaving instructions
        pipeline[0] = -1
        cycle_counter = cycle_counter + 1;
        print ("Current cycle: " + str(cycle_counter))
        print ("Current state: " + str(pipeline))
############################################################################################################

############################################################################################################
# MEMORY MANAGEMENT
############################################################################################################		
def memory_initialize():
    # code to initialize memory
    print ("test")

def memory_store_at_addr(addr, value):
	# code to store value at addr
    print ("test")
    
def memory_load_from_addr(addr):
	# code to load from addr
    print ("test")
############################################################################################################


if __name__ == "__main__":
    #main(sys.argv[1:])
    main()