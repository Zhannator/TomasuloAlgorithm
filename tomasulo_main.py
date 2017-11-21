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
timing_table = tomasulo_timing_table.TTobject() # doesn't need to be initialized
load_store_queue = [] # doesn't need to be initialized

############################################################################################################
# MAIN
############################################################################################################		
def main(input_filename): # argv is a list of command line arguments
    # GLOBAL CONTROL LOGIC SIGNALS (DEFAULTS ARE 0)
    available_int_fu = 0
    timing_table_entry_index = 0
    memory_is_in_use = 0 # will be incremented by cycles_in_mem and decremented by 1's
    memory_buffer = [] # [address, value]
    cdb_in_use = 0 # will be 1 or 0
    commit_in_use = 0 # will be 1 or 0
    arf_buffer = []
    
    #-------------------------------------------------
    # Structures and Parameters Initialization
    #-------------------------------------------------

    # initialize registers and memory
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
    #load_store_queue.load_store_queue_initialize()
    
    
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
        
        # UPDATE MEMORY USAGE
        if memory_is_in_use != 0:
            memory_is_in_use = memory_is_in_use - 1
            if memory_is_in_use == 0 and memory_buffer != []:
                memory.mem_write(memory_buffer[0], memory_buffer[1])
                memory_buffer = []
                print "Update memory location " + str(memory_buffer[0]) + " to " + str(memory_buffer[1])
        
        # UPDATE ARFobject
        if arf_buffer != []:
            arf_write(arf_buffer[0], arf_buffer[1])
            arf_buffer = []
        
        # UPDATE CDB USAGE
        if cdb_in_use == 1:
            cdb_in_use = 0
        
        # UPDATE CDB USAGE
        if commit_in_use == 1:
            commit_in_use = 0
        
        # SEPARATE FROM ROB
        
        #---------------------------------------------------------------------
        # ISSUE STAGE
        #---------------------------------------------------------------------
        # can_issue_new_instuction = (available_instuction_in_instruction_buffer) & (available_rob_entry) &  (available_rs_entry)
        rob_dest = "-" # signifies that an instruction wasn't issued on this cycle if stays to be "-"
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
            if instruction_id in ["ADD", "ADDI", "SUB", "BEQ", "BNE"]: # check int_adder_rs
                rs_index = rs.rs_available("int_adder_rs")
                available_rs_entry = (rs_index != -1)
                if available_rs_entry:
                    # add entry
                    # check if we have values of qj and qk
                    if instruction_id in ["BEQ", "BNE"]:
                        # handle branch instructions 
                        reg1 = get_current_reg_info(instruction_parsed[1]) # reg_name
                        reg2 = get_current_reg_info(instruction_parsed[2]) # reg_name
                        rob_dest = rob.rob_instr_add(instruction, "-", timing_table_entry_index)
                        rat.int_rat_update(instruction_parsed[1], rob_dest) # need to update rat
                    else:
                        reg1 = get_current_reg_info(instruction_parsed[2]) # reg_name
                        reg2 = get_current_reg_info(instruction_parsed[3]) # reg_name
                        rob_dest = rob.rob_instr_add(instruction, instruction_parsed[1], timing_table_entry_index)
                        rat.int_rat_update(instruction_parsed[1], rob_dest) # need to update rat
                    timing_table_entry_index = timing_table_entry_index + 1
                    rs.rs_add("int_adder_rs", rs_index, instruction_id, rob_dest, reg1[0], reg2[0], reg1[1], reg2[1]) # rs_name, i, op, dest, vj, vk, qj, qk
                    timing_table.timing_table_add(PC, instruction, cycle_counter)
                    PC = PC + 4
            elif instruction_id in ["ADD.D", "SUB.D"]: # check fp_adder_rs
                rs_index = rs.rs_available("fp_adder_rs")
                available_rs_entry = (rs_index != -1)
                if available_rs_entry:
                    # add entry
                    # check if we have values of qj and qk
                    reg1 = get_current_reg_info(instruction_parsed[2]) # reg_name
                    reg2 = get_current_reg_info(instruction_parsed[3]) # reg_name
                    rob_dest = rob.rob_instr_add(instruction, instruction_parsed[1], timing_table_entry_index)
                    rat.fp_rat_update(instruction_parsed[1], rob_dest) # need to update rat
                    timing_table_entry_index = timing_table_entry_index + 1
                    rs.rs_add("fp_adder_rs", rs_index, instruction_id, rob_dest, reg1[0], reg2[0], reg1[1], reg2[1]) # rs_name, i, op, dest, vj, vk, qj, qk
                    timing_table.timing_table_add(PC, instruction, cycle_counter)
                    PC = PC + 4
            elif instruction_id in ["MULT.D"]: # check fp_multiplier_rs
                rs_index = rs.rs_available("fp_multiplier_rs")
                available_rs_entry = (rs_index != -1)
                if available_rs_entry:
                    # add entry
                    #check if we have values of qj and qk
                    reg1 = get_current_reg_info(instruction_parsed[2]) # reg_name
                    reg2 = get_current_reg_info(instruction_parsed[3]) # reg_name
                    rob_dest = rob.rob_instr_add(instruction, instruction_parsed[1], timing_table_entry_index)
                    rat.fp_rat_update(instruction_parsed[1], rob_dest) # need to update rat
                    timing_table_entry_index = timing_table_entry_index + 1
                    rs.rs_add("fp_multiplier_rs", rs_index, instruction_id, rob_dest, reg1[0], reg2[0], reg1[1], reg2[1]) # rs_name, i, op, dest, vj, vk, qj, qk
                    timing_table.timing_table_add(PC, instruction, cycle_counter)
                    PC = PC + 4
            elif instruction_id in ["LD", "SD"]:
                print "HANDLE LD AND SD TODO"
            else:
                print "Invalid instuction!"
                exit(1)
 
        # cycle through ROB
        rob_entry = rob.rob_head_node() 
        while rob_entry != -1:
            rob_entry_state = rob.rob_get_state(rob_entry)
            rob_entry_instruction_id = rob_get_instruction_id(rob_entry)
            if rob_entry_state == "WB":
                #---------------------------------------------------------------------
                # WB -> COMMIT STAGE
                #---------------------------------------------------------------------
                #can_move_from_wb_to_commit = (!commit_in_use) & (rob_top_instruction_ready_to_commit)
                if commit_in_use == 0 and rob.rob_top_instruction_ready_to_commit(rob_entry):
                    if rob_entry_instruction_id in ["ADD", "ADDI", "SUB", "ADD.D", "SUB.D", "MULT.D", "LD"]: 
                        #set arf buffer
                        arf_buffer = [rob.rob_get_destination(rob_entry), rob.rob_get_value(rob_entry)]
                        #clear rob entry
                        rob.rob_commit()
                    elif instruction_id in ["SD"] and memory_is_in_use == 0:
                        #set memory_buffer
                        memory_buffer = [rob.rob_get_destination(rob_entry), rob.rob_get_value(rob_entry)]
                        #update timing table
                        timing_table.timing_table_update(rob.rob_get_tt_index(rob_entry), "COMMIT", cycle_counter, load_store_unit_properties["cycles_in_mem"])
                        #set memory in use
                        memory_is_in_use = load_store_unit_properties["cycles_in_mem"]
                        #clear rob entry
                        rob.rob_commit()
                    elif instruction_id in ["BEQ", "BNE"]:
                        #clear rob entry
                        rob.rob_commit()
                    commit_in_use = 1
            elif rob_entry_state == "MEM":
                #---------------------------------------------------------------------
                # MEM -> WB
                #---------------------------------------------------------------------
                #can_move_from_mem_to_wb_stage = (forwarding_flag_set) & ((cycle_counter-mem_s) == 1)  & (!cdb_will_be_in_use_next_cycle) or (!forwarding_flag_set) & ((cycle_counter-mem_s) == fu_mem_cycles) & (!cdb_will_be_in_use_next_cycle)

            elif rob_entry_state == "EX" and rob_entry_instruction_id == "LD":  
                #---------------------------------------------------------------------
                # EX -> MEM
                #---------------------------------------------------------------------
                #can_move_from_ex_to_mem_stage = (ld_instuction) & ((cycle_counter-ex_s) == fu_execution_cycles) & (!memory_will_be_in_use_next_cycle)
                
            elif rob_entry_state == "EX" and rob_entry_instruction_id != "LD":    
                #---------------------------------------------------------------------
                # EX -> WB STAGE
                #---------------------------------------------------------------------            
                #can_move_from_ex_to_wb_stage = (!ld_instuction) & ((cycle_counter-ex_s) == fu_execution_cycles) & (!cdb_will_be_in_use_next_cycle)
                
            elif rob_entry_state == "ISSUE":    
                #---------------------------------------------------------------------
                # ISSUE -> EX
                #---------------------------------------------------------------------            
                #can_move_to_ex_stage = (alu_int_instruction) & (no_register_dependencies) & (available_int_fu) or (!alu_int_instruction) & (no_register_dependencies)
                if rob_entry_instruction_id == "ADD"
                elif rob_entry_instruction_id == "ADDI":
                elif rob_entry_instruction_id == "SUB":
                elif rob_entry_instruction_id == "ADD.D":
                elif rob_entry_instruction_id == "SUB.D":
                elif rob_entry_instruction_id == "MULT.D":
                elif rob_entry_instruction_id == "BEQ": # resolve branch using int adder
                elif rob_entry_instruction_id == "BNE": # resolve branch using int adder
                elif instruction_id in ["SD", "LD"]: # calculate address
            
                
            
            rob_entry = rob.next(rob_entry, rob_dest)
            
    
    rob.rob_print()
    rs.rs_print() 
    timing_table.time_table_print()
    memory.mem_print_non_zero_values()
    arf.arf_print()
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