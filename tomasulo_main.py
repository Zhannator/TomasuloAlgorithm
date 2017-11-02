#!/usr/bin/python
# -*- coding: utf-8 -*-

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

from sys import argv

# Global Variables / Defaults
num_rob_entries = 128 # # of ROB entries
int_adder_properties = {
    "num_rs" : 2,
    "cycles_in_ex" : 1,
    "num_fus" : 1
}
fp_adder_properties = {
    "num_rs" : 3,
    "cycles_in_ex" : 3,
    "num_fus" : 1
}
fp_multiplier_properties = {
    "num_rs" : 2,
    "cycles_in_ex" : 20,
    "num_fus" : 1
}
load_store_unit_properties = {
    "num_rs" : 3,
    "cycles_in_ex" : 1,
    "cycles_in_mem" : 4,
    "num_fus" : 1
}
instruction_buffer = ["Add.d R1, R2, R3", "Add.d R1, R2, R3", "Add.d R1, R2, R3", "Add.d R1, R2, R3", "Add.d R1, R2, R3"]
memory = [] # needs to be initialized, 256B(64W), needs its own function on how to reference locations in mem by word/byte
int_registers = [] # needs to be initialized, 32 registers by DLX standard
fp_registers = [] # needs to be initialized, 32 registers by DLX standard
int_rat = [] # needs to be initialized, same size as ARF
fp_rat = [] # needs to be initialized, same size as ARF
rs = { # needs to be initialized
    "int_adder_rs" : [{
        "busy" : "no",
        "op" : "",
        "dest" : "",
        "Vj" : "",
        "Vk" : "",
        "Qj" : 0,
        "Qk" : 0
    }],
    "fp_adder_rs" : [{
        "busy" : "no",
        "op" : "",
        "dest" : "",
        "Vj" : "",
        "Vk" : "",
        "Qj" : 0,
        "Qk" : 0
    }],
    "fp_multiplier_rs" : [{
        "busy" : "no",
        "op" : "",
        "dest" : "",
        "Vj" : "",
        "Vk" : "",
        "Qj" : 0,
        "Qk" : 0
    }]
}
rob = [{ # needs to be initialized
    "busy" : 0,
    "instruction" : "",
    "state" : "",
    "destination" : 0, # “dest" field of a store instruction records its location in the load/store queue
    "value" : 0
}]
#load_store_queue = [{ # TODO!!! NEED TO BE IMPLEMENTED AS A QUEUE: https://docs.python.org/2/library/queue.html
#    "addr" : 0,
#    "value" : 0
#}]
timing_table = [] # needs to be updated during execution time (instruction, column for each stage)


############################################################################################################
# MAIN
############################################################################################################		
def main(input_filename): # argv is a list of command line arguments
    # initialise registers and memory
    reg_initialize()
    mem_initialize()
    # set configurations of the hw units and assembly instructions
    input_file_decoder(input_filename)
    # initialize rat
    rat_initialize()
    # initialize rs
    rs_initialize()
    # initialize rob
    rob_initialize()
    # initialize load/store queue
    #load_store_queue_initialize() #TODO
    
	# assume for now everything takes one cycle
	# assume no dependencies
	
    cycle_counter = 0;
    instruction_counter = 0;
    pipeline = [-1, -1, -1, -1, -1] # 5 stages: ISSUE(0), EX(1), MEM(2), WB(3), and COMMIT(4)
    PC = 0 # in words
    
	
    for instruction in instruction_buffer:
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
# INPUT FILE DECODER
############################################################################################################		
def input_file_decoder(input_filename):
    input_file = open(input_filename, 'r')
    for line_not_split in input_file:
        line = line_not_split.split(" ")
        if(line[0] == "int_adder"):
            # set int_adder_properties
            int_adder_properties["num_rs"] = int(line[1])
            int_adder_properties["cycles_in_ex"] = int(line[2])
            int_adder_properties["num_fus"] = int(line[3])
        elif(line[0] == "fp_adder"):
            # set fp_adder_properties
            fp_adder_properties["num_rs"] = int(line[1])
            fp_adder_properties["cycles_in_ex"] = int(line[2])
            fp_adder_properties["num_fus"] = int(line[3])
        elif(line[0] == "fp_multiplier"):
            # set fp_multiplier_properties
            fp_multiplier_properties["num_rs"] = int(line[1])
            fp_multiplier_properties["cycles_in_ex"] = int(line[2])
            fp_multiplier_properties["num_fus"] = int(line[3])
        elif(line[0] == "load_store_unit"):
            # set load_store_unit_properties
            load_store_unit_properties["num_rs"] = int(line[1])
            load_store_unit_properties["cycles_in_ex"] = int(line[2])
            load_store_unit_properties["cycles_in_mem"] = int(line[3])
            load_store_unit_properties["num_fus"] = int(line[4])
        elif(line[0] == "rob_entries"):
            # set num_rob_entries
            num_rob_entries = int(line[1])
        elif(line[0] == "reg"):
            # set register value
            reg_write(line[1], line[2])
        elif(line[0] == "mem"):
            # set memory value
            mem_write(line[1], line[2])
        else:
            # instruction
            instruction_buffer.append(line_not_split)
############################################################################################################

############################################################################################################
# ARCHITECTURE REGISTER FILE MANAGEMENT
############################################################################################################		
def reg_initialize():
    # code to initialize memory
    global int_registers
    global fp_registers
    int_registers = [0]*32
    fp_registers = [0]*32

def reg_write(register, value):
	# code to store value at addr
    # register, value are strings
    global int_registers
    global fp_registers
    if register[0] == 'R':
        reg_num = int(register.split('R')[1])
        if reg_num < 32 and reg_num != 0:
            int_registers[reg_num] = int(value)
        else:
            print "Invalid register!"
            exit(0)
    elif register[0] == 'F':
        reg_num = int(register.split('F')[1])
        if reg_num < 32:
            fp_registers[reg_num] = float(value)
        else:
            print "Invalid register!"
            exit(0)
    else:
        print ("Invalid register!")
        exit(0)
    
def reg_read(register):
	# code to load from addr
    # register is string
    global int_registers
    global fp_registers
    if register[0] == 'R':
        reg_num = int(register.split('R')[1])
        if reg_num < 32:
            return int_registers[reg_num]
        else:
            print "Invalid register!"
            exit(0)
    elif register[0] == 'F':
        reg_num = int(register.split('F')[1])
        if reg_num < 32:
            return fp_registers[reg_num]
        else:
            print "Invalid register!"
            exit(0)
    else:
        print ("Invalid register!")
        exit(0)
############################################################################################################

############################################################################################################
# MEMORY MANAGEMENT
############################################################################################################		
def mem_initialize():
    # code to initialize memory
    global memory
    memory = [0]*64 # 265B (64W)

def mem_write(addr, value):
	# code to store value at addr
    # addr, value are strings
    # addr must be specified in byte
    global memory
    memory[int(int(addr)/4)] = float(value)
    
def mem_read(addr):
	# code to load from addr
    # addr is string
    # addr must be specified in byte
    global memory
    return memory[int(int(addr)/4)]
############################################################################################################

############################################################################################################
# INITIALIZING OTHER UNITS
############################################################################################################
def rat_initialize():
    # initialize rat
    global int_rat
    global fp_rat
    for i in range(0, 32):
        int_rat.append("R" + str(i))
        fp_rat.append("F" + str(i))
    
def rs_initialize():
    # initialize rs based on configs of FUs
    global rs
    rs["int_adder_rs"] = rs["int_adder_rs"]*int_adder_properties["num_rs"]
    rs["fp_adder_rs"] = rs["fp_adder_rs"]*fp_adder_properties["num_rs"]
    rs["fp_multiplier_rs"] = rs["fp_multiplier_rs"]*fp_multiplier_properties["num_rs"]   
     
def rob_initialize():
    # initialize rob
    global rob
    rob = rob*num_rob_entries
    print rob
    
#def load_store_queue_initialize():
#    # initialize load/store queue
#    print "TODO"
    
def timing_table_update():
    # TODO!!!
    print "TODO"
############################################################################################################
    
if __name__ == "__main__":
    if len(argv) > 1:
        main(argv[1]) # python2.7 tomasulo_main.py input_file.txt
    else:
        print "Please specify input file!"
        exit(0)