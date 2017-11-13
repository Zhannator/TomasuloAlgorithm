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

# GLOBAL PARAMETERS
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

# GLOBAL STRUCTURES
instruction_buffer = []
memory = tomasulo_mem.MEMobject() # 256B(64W), needs its own function on how to reference locations in mem by word/byte
arf = tomasulo_arf.ARFobject()
rat = tomasulo_rat.RATobject()
rs = tomasulo_rs.RSobject()
rob = tomasulo_rob.ROBobject()
timing_table = tomasulo_timing_table.TTobject()
load_store_queue = []

# GLOBAL CONTROL LOGIC SIGNALS (DEFAULTS ARE 0)
available_int_fu = 0

memory_will_be_in_use_next_cycle = 0
cdb_will_be_in_use_next_cycle = 0

############################################################################################################
# MAIN
############################################################################################################		
def main(input_filename): # argv is a list of command line arguments
    #-------------------------------------------------
    # Structures and Parameters Initialization
    #-------------------------------------------------

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
    #load_store_queue_initialize()
    
    #-------------------------------------------------
    # PIPELINE V1: assume only # ALU Instructions and no dependencies 
    #-------------------------------------------------
    
    # each loop run is a new cycle, exits when all the instructions exitited pipeline and instruction buffer has been used up
    PC = 0 # instruction buffer index, incremented by 4
    cycle_counter = 0
    while(1):
        # print results and exit if rob is empty and instruction_buffer is exerted
        if rob.rob_empty() and ((PC/4) > len(instruction_buffer)):
            timing_table.time_table_print()
            arf.arf_print()
            memory.mem_print_non_zero_values()
            exit(0)
            
        # INCREMENT CYCLE
        cycle_counter = cycle_counter + 1
        
        # can_issue_new_instuction = (available_instuction_in_instruction_buffer) & (available_rob_entry) &  (available_rs_entry)
        available_instuction_in_instruction_buffer = ((PC/4) < len(instruction_buffer))
        print "available_instuction_in_instruction_buffer: " + str(available_instuction_in_instruction_buffer)
        available_rob_entry = (rob.rob_available() == 1)
        print "available_rob_entry: " + str(available_rob_entry)
        if available_instuction_in_instruction_buffer and available_rob_entry:
            # get insturction
            instruction = instruction_buffer[(PC/4)]
            print "instruction: " + instruction
            instruction_parsed = instruction.split(" ")
            instruction_id = instruction_parsed[0]
            # check if there is an available rs entry based on instruction op
            rs_index = 0          
            if instruction_id in ["ADD", "ADDI", "SUB"]: # check int_adder_rs
                rs_index = rs.rs_available("int_adder_rs")
                available_rs_entry = (rs_index != -1)
                if available_rs_entry:
                    # add entry
                    # check if we have values of qj and qk
                    reg1 = get_current_reg_info(instruction_parsed[2]) # reg_name
                    reg2 = get_current_reg_info(instruction_parsed[3]) # reg_name
                    rob_dest = rob.rob_instr_add(instruction)
                    rs.rs_add("int_adder_rs", rs_index, instruction_id, rob_dest, reg1[0], reg2[0], reg1[1], reg2[1]) # rs_name, i, op, dest, vj, vk, qj, qk
                    PC = PC + 4
            elif instruction_id in ["ADD.D", "SUB.D"]: # check fp_adder_rs
                rs_index = rs.rs_available("fp_adder_rs")
                available_rs_entry = (rs_index != -1)
                if available_rs_entry:
                    # add entry
                    # check if we have values of qj and qk
                    reg1 = get_current_reg_info(instruction_parsed[2]) # reg_name
                    reg2 = get_current_reg_info(instruction_parsed[3]) # reg_name
                    rob_dest = rob.rob_instr_add(instruction)
                    rs.rs_add("fp_adder_rs", rs_index, instruction_id, rob_dest, reg1[0], reg2[0], reg1[1], reg2[1]) # rs_name, i, op, dest, vj, vk, qj, qk
                    PC = PC + 4
            elif instruction_id in ["MULT.D"]: # check fp_multiplier_rs
                rs_index = rs.rs_available("fp_multiplier_rs")
                available_rs_entry = (rs_index != -1)
                if available_rs_entry:
                    # add entry
                    #check if we have values of qj and qk
                    reg1 = get_current_reg_info(instruction_parsed[2]) # reg_name
                    reg2 = get_current_reg_info(instruction_parsed[3]) # reg_name
                    rob_dest = rob.rob_instr_add(instruction)
                    rs.rs_add("fp_multiplier_rs", rs_index, instruction_id, rob_dest, reg1[0], reg2[0], reg1[1], reg2[1]) # rs_name, i, op, dest, vj, vk, qj, qk
                    PC = PC + 4
            elif instruction_id in ["LD", "SD"]:
                print "HANDLE LD AND SD TODO"
            elif instruction_id in ["BEQ", "BNE"]:
                print "HANDLE BEQ AND BNE TODO"
            else:
                print "Invalid instuction!"
                exit(1)

        if PC == 12:
            print "END TEST"
            print
            rob.rob_print()
            print
            rs.rs_print()
            exit(0)
        
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
        line_not_split = line_not_split.upper().split("\n")[0]
        line = line_not_split.upper().split(" ")
        if(line[0] == "INT_ADDER"):
            # set int_adder_properties
            int_adder_properties["num_rs"] = int(line[1])
            int_adder_properties["cycles_in_ex"] = int(line[2])
            int_adder_properties["num_fus"] = int(line[3])
        elif(line[0] == "FP_ADDER"):
            # set fp_adder_properties
            fp_adder_properties["num_rs"] = int(line[1])
            fp_adder_properties["cycles_in_ex"] = int(line[2])
            fp_adder_properties["num_fus"] = int(line[3])
        elif(line[0] == "FP_MULTIPLIER"):
            # set fp_multiplier_properties
            fp_multiplier_properties["num_rs"] = int(line[1])
            fp_multiplier_properties["cycles_in_ex"] = int(line[2])
            fp_multiplier_properties["num_fus"] = int(line[3])
        elif(line[0] == "LOAD_STORE_UNIT"):
            # set load_store_unit_properties
            load_store_unit_properties["num_rs"] = int(line[1])
            load_store_unit_properties["cycles_in_ex"] = int(line[2])
            load_store_unit_properties["cycles_in_mem"] = int(line[3])
            load_store_unit_properties["num_fus"] = int(line[4])
        elif(line[0] == "ROB_ENTRIES"):
            # set num_rob_entries
            num_rob_entries = int(line[1])
        elif(line[0] == "REG"):
            # set register value
            arf.reg_write(line[1], line[2])
        elif(line[0] == "MEM"):
            # set memory value
            memory.mem_write(line[1], line[2])
        elif(line_not_split != "" and line[0] != "#"): # if it isn't 
            # instruction
            instruction_buffer.append(line_not_split)
############################################################################################################

############################################################################################################
# CONTROL LOGIC
############################################################################################################
def control_logic():
    # needs to be generated at the beginning of each cycle and will be used to make decisions for pipeline
    
    ######## 1) only for next instructin in buffer ########
    
    #can_issue_new_instuction = (available_instuction_in_instruction_buffer) &  (available_rs_entry) & (available_rob_entry)
    
    ######## 2) for each instruction in the issue stage going to ex stage ########
    
    #can_move_to_ex_stage = (alu_int_instruction) & (no_register_dependencies) & (available_int_fu) or (!alu_int_instruction) & (no_register_dependencies)
    
    ######## 3.1) for each instruction in the ex stage going to mem stage ########
    
    #can_move_from_ex_to_mem_stage = (ld_instuction) & ((cycle_counter-ex_s) == fu_execution_cycles) & (!memory_will_be_in_use_next_cycle)
    
    ######## 3.2) for each instruction in the ex stage going to wb stage ########
    
    #can_move_from_ex_to_wb_stage = (!ld_instuction) & ((cycle_counter-ex_s) == fu_execution_cycles) & (!cdb_will_be_in_use_next_cycle)
    
    ######## 4) for each instruction in the mem stage ########
    
    #can_move_from_mem_to_wb_stage = (forwarding_flag_set) & ((cycle_counter-mem_s) == 1)  & (!cdb_will_be_in_use_next_cycle) or (!forwarding_flag_set) & ((cycle_counter-mem_s) == fu_mem_cycles) & (!cdb_will_be_in_use_next_cycle)
    
    ######## 5) for each instruction in the wb stage ########
    
    #can_move_from_wb_to_commit = (!memory_will_be_in_use_next_cycle) & (rob_top_instruction_ready_to_commit)
    
    ######## 6) for each instruction in the commit stage waiting to exit pipeline ########
       
    #can_exit_pipeline = ((cycle_counter-mem_s) == fu_mem_cycles)
    
    print "CONTROL LOGIC TODO"
############################################################################################################

############################################################################################################
# EXTRA FUNCTIONS
############################################################################################################
def get_current_reg_info(reg_name): # returns [v, q]
    # get the operands if they are available in either the registers or the ROB
    
    # check RAT
    if reg_name.startswith("R"):
        reg_value = rat.int_rat_get(reg_name)
    else:
        reg_value = rat.fp_rat_get(reg_name)
        
    if reg_value.startswith("ROB"): # if ROB -> 
        rob_entry_value = rob.rob_get_value(reg_value)
        if str(rob_entry_value) == "-": # if ROB# value is ready -> pull value from ROB
            return ["-", reg_value]
        else: # if ROB# value not ready -> return ROB name
            return [rob_entry_value, "-"]    
    else: # if R or F -> 
        # pull value from ARFobject
        return [arf.reg_read(reg_value), "-"]
    
    print "GET CURRENT REG INFO TODO"
    
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
        exit(1)