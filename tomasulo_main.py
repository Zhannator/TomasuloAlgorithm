#!/usr/bin/python
# -*- coding: utf-8 -*-

# public libraries
from sys import argv
import numpy as np

# private libraries
import tomasulo_rat
import tomasulo_rs
import tomasulo_arf
import tomasulo_mem
import tomasulo_rob
import tomasulo_timing_table

#
alu_instructions_int = ["Add", "Addi", "Sub"]
alu_instructions_fp = ["Add.d", "Sub.d", "Mult.d"]
# Global Variables / Defaults
num_rob_entries = 128 # number of ROB entries
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
rob = tomasulo_rob.ROBobject()
load_store_queue = []
timing_table = tomasulo_timing_table.TTobject()

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
    rob.rob_initialize(num_rob_entries)
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
                    # check if ROB entry is available
                    if rob.rob_instr_add(instruction_buffer[PC]) != -1:
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
                    if rob.rob_instr_add(instruction_buffer[PC]) != -1:                   
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
        elif(line_not_split != ""):
            # instruction
            instruction_buffer.append(line_not_split)
############################################################################################################

############################################################################################################
# ROB TEMPORARY
############################################################################################################
def rob_empty():
    # return 1 if rob is empty, else 0
    return 1
############################################################################################################

############################################################################################################
# CDB TEMPORARY
############################################################################################################
def cdb():
    # when value is ready in RS -> broadcast values to ROB, RS
    # other situations
    print "CDB TODO"
############################################################################################################

if __name__ == "__main__":
    if len(argv) > 1:
        main(argv[1]) # python2.7 tomasulo_main.py input_file.txt
    else:
        print "Please specify input file!"
        exit(0)