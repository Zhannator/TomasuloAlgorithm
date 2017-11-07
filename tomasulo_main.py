#!/usr/bin/python
# -*- coding: utf-8 -*-

from sys import argv
import tomasulo_rat
import tomasulo_rs
import tomasulo_arf
import tomasulo_mem

#
alu_instructions_int = ["Add", "Addi", "Sub"]
alu_instructions_fp = ["Add.d", "Sub.d", "Mult.d"]
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
memory = tomasulo_mem.MEMobject() # 256B(64W), needs its own function on how to reference locations in mem by word/byte
arf = tomasulo_arf.ARFobject()
rat = tomasulo_rat.RATobject()
rs = tomasulo_rs.RSobject()
rob = []
load_store_queue = []
timing_table = [] # needs to be updated during execution time (pc, instruction, column for each stage)

############################################################################################################
# MAIN
############################################################################################################		
def main(input_filename): # argv is a list of command line arguments
    # initialise registers and memory
    arf.reg_initialize()
    memory.mem_initialize()
    # set configurations of the hw units and assembly instructions
    input_file_decoder(input_filename)
    # initialize rat
    rat.rat_initialize()
    # initialize rs
    rs.rs_initialize(int_adder_properties["num_rs"], fp_adder_properties["num_rs"], fp_multiplier_properties["num_rs"])
    # initialize rob
    rob_initialize()
    # initialize load/store queue
    #load_store_queue_initialize() #TODO
    
    #-------------------------------------------------
    # Pipeline V1: assume only # ALU Instructions and no dependencies 
    #-------------------------------------------------
    cycle_counter = 0;
    PC = 0 # buffer index, incremented by 1
    
    # read instruction from instruction buffer
    while(1):
        # print results and exit if rob is empty and instruction_buffer is exerted
        if rob_empty() and (PC >= len(instruction_buffer)):
            time_table_print()
            exit(0)
        
        # INCREMENT CYCLE
        cycle_counter = cycle_counter + 1
        
        #-----------------------------------------------------
        # ISSUE
        #-----------------------------------------------------
        if PC < len(instruction_buffer):
            # parse instruction 
            parsed_instruction = instruction_buffer[PC].split(" ")
            # if alu instruction
            if parsed_instruction[0] in alu_instructions_int:
                print "THIS IS AN INTEGER ALU INSTRUCTION"
                # check int RS
                i = rs.rs_available("int_adder_rs")
                if i != -1: # if rs is available
                    #add instuction
                    rs.rs_add("int_adder_rs", i, parsed_instruction[0], parsed_instruction[1], parsed_instruction[2], parsed_instruction[3])
                    # add entry to timing table
                    timing_table_add(PC, parsed_instruction[0], cycle_counter)
                    PC = PC + 1
            elif parsed_instruction[0] in alu_instructions_fp:
                print "THIS IS A FP ALU INSTRUCTION"
                rs_name = "fp_adder_rs"
                if parsed_instruction[0] == "Mult.d":
                    # if multiplier
                    rs_name = "fp_multiplier_rs"
                i = rs.rs_available(rs_name)
                if i != -1: # if rs is available
                    # check if ROB entry is available
                
                    #add instuction 
                    rs.rs_add(rs_name, i, parsed_instruction[0], parsed_instruction[1], parsed_instruction[2], parsed_instruction[3])
                    # add entry to timing table
                    timing_table_add(PC, parsed_instruction[0], cycle_counter)
                    PC = PC + 1
                else:
                    print("RS is full")
                    print("PC: " + str(PC))
                    print rs.rs
                    exit(0)
            else:
                print "THIS IS NOT AN ALU INSTRUCTION. EXITING..."
                exit(0)
            # if resources available: RS entry, ROB entry
                # read RAT, read (available sources), update RAT
                # write to RS and ROB
            # else stall
        
        #-----------------------------------------------------
        # EX
        #-----------------------------------------------------
        # wait for all operands to arrive: check RS tables
            # complete to use functional units
            # execute
        #-----------------------------------------------------
        # MEM
        #-----------------------------------------------------
        # broadcast result on CDB: any dependants will grab the value
        # write result back to RS and ROB entries
        # mark ready/finished bit in ROB
        #-----------------------------------------------------
        # WB
        #-----------------------------------------------------
        # when instruction is the oldest in the ROB (ROB head)
            # write result if ready/finished bit is set (memory or register)
        # advance ROB-head to next instruction
    #-------------------------------------------------
    
    #-------------------------------------------------
    # Simple Pipeline: assume everything stage takes one cycle and no dependencies
    #-------------------------------------------------
    #cycle_counter = 0;
    #pipeline = [-1, -1, -1, -1, -1] # 5 stages: ISSUE(0), EX(1), MEM(2), WB(3), and COMMIT(4)
    #PC = 0 # in bytes

    #for instruction in instruction_buffer:
    #    #leaving_instruction = pipeline[4]
    #    for i in range(4, 0, -1): # 5 stages
    #        pipeline[i] = pipeline[i-1] # need to accomodate for leaving instructions
    #    # get new instruction
    #    pipeline[0] = PC;
    #    PC = PC + 4;
    #    cycle_counter = cycle_counter + 1;
    #    # advance instructions in pipeline
    #    print ("Current cycle: " + str(cycle_counter))
    #    print ("Current state: " + str(pipeline))
    # advance leftover instructions in pipeline
    #for j in range(0, 5):
    #    #leaving_instruction = pipeline[4]
    #    for i in range(4, 0, -1): # 5 stages
    #        pipeline[i] = pipeline [i-1] # need to accomodate for leaving instructions
    #    pipeline[0] = -1
    #    cycle_counter = cycle_counter + 1;
    #    print ("Current cycle: " + str(cycle_counter))
    #    print ("Current state: " + str(pipeline))
    #-------------------------------------------------
############################################################################################################

############################################################################################################
# INPUT FILE DECODER
############################################################################################################		
def input_file_decoder(input_filename):
    global int_adder_properties
    global fp_adder_properties
    global fp_multiplier_properties
    global num_rob_entries
    global instruction_buffer
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
            arf.reg_write(line[1], line[2])
        elif(line[0] == "mem"):
            # set memory value
            memory.mem_write(line[1], line[2])
        else:
            # instruction
            instruction_buffer.append(line_not_split)
############################################################################################################

############################################################################################################
# ROB
############################################################################################################
def rob_initialize():
    # initialize rob
    print #TODO

def rob_empty():
    # return 1 if rob is empty, else 0
    return 1
############################################################################################################

############################################################################################################
# CDB
############################################################################################################
#def cdb():
############################################################################################################

############################################################################################################
# LOAD/STORE QUEUE
############################################################################################################
#def load_store_queue_initialize():
#    # initialize load/store queue
#    print "TODO"
############################################################################################################

############################################################################################################
# TIMING TABLE
############################################################################################################ 
def timing_table_add(PC, instruction, clock_cycle):
    timing_table_entry = {
        "PC" : PC,
        "instruction" : instruction,
        "issue" : clock_cycle,
        "ex_start" : 0,
        "ex_finish" : 0,
        "mem_start" : 0,
        "mem_finish" : 0,      
        "wb" : 0,
        "commit" : 0
    }
    timing_table.append(timing_table_entry.copy())
    print "TODO"

def timing_table_update():
    # TODO!!!
    print "TODO"
def time_table_print():
    print rs.rs
    print "TODO"
############################################################################################################
    
if __name__ == "__main__":
    if len(argv) > 1:
        main(argv[1]) # python2.7 tomasulo_main.py input_file.txt
    else:
        print "Please specify input file!"
        exit(0)