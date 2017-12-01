#!/usr/bin/python
# -*- coding: utf-8 -*-

# public libraries
from sys import argv

# private libraries
import tomasulo_rat
import tomasulo_rs
import tomasulo_arf
import tomasulo_mem
import tomasulo_rob
import tomasulo_timing_table
import tomasulo_load_store_queue

# GLOBAL PARAMETERS
num_rob_entries = 128 # number of ROB entries
int_adder_properties = {
    "num_rs" : 2,
    "cycles_in_ex" : 1,
    "num_fus" : 2
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
lsq = tomasulo_load_store_queue.LSQobject()

############################################################################################################
# MAIN
############################################################################################################		
def main(input_filename): # argv is a list of command line arguments
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
    # initialize load store queue
    lsq.lsq_initialize(load_store_unit_properties["num_rs"])    
        
    # GLOBAL CONTROL LOGIC SIGNALS
    available_int_fu = int_adder_properties["num_fus"] # decremented if someone starts using it, incremented if someone exits ex stage; if 0 - > no fu available
    available_ls_fu = load_store_unit_properties["num_fus"] # decremented if someone starts using it, incremented if someone exits ex stage; if 0 - > no fu available
    timing_table_entry_index = 0
    memory_is_in_use = 0 # will be incremented by cycles_in_mem and decremented by 1's
    memory_buffer = [] # [address, value]
    cdb_in_use = 0 # will be 1 or 0
    arf_buffer = []
    cdb_buffer = [] # treated as a priority queue, older buffer entries are at the top (smaller index)
    ls_buffer = [] # once addresses are calculated -> they are written to lsq_add
    stall_instruction_buffer = 0 # is 1 when want to stall instruction buffer
    branch_buffer = [] # [branch resolution, ready_cycle, rob_entry]
    int_adder_fu_timer = [] # needed to keep track when int adder fus get freed
    
    #-------------------------------------------------
    # PIPELINE
    #-------------------------------------------------
    
    # each loop run is a new cycle, exits when all the instructions exitited pipeline and instruction buffer has been used up
    PC = 0 # instruction buffer index, incremented by 4
    cycle_counter = 0
    while(1):
		# INCREMENT CYCLE
        cycle_counter = cycle_counter + 1
        
        # RESET number of available fp fus
        available_fp_adder_fu = fp_adder_properties["num_fus"] # fp fus are pipelined, this number corresponds to how many fp adder instructions can be moved to ex stage in the same cycle; incremented when
        available_fp_mult_fu = fp_multiplier_properties["num_fus"] # fp fus are pipelined, this number corresponds to how many fp mult instructions can be moved to ex stage in the same cycle
		
        # UPDATE MEMORY USAGE
        #print "********* MEMORY BUFFER: " + str(memory_buffer) + " *********"
        if memory_is_in_use != 0:
            memory_is_in_use = memory_is_in_use - 1
            if memory_is_in_use == 0 and memory_buffer != []:
                memory.mem_write(memory_buffer[0], memory_buffer[1])
                #dequeue the lsq
                lsq.lsq_dequeue(memory_buffer[2])
                #print "Update memory location " + str(memory_buffer[0]) + " to " + str(memory_buffer[1])
                memory_buffer = []
                        
        # UPDATE ARFobject
        if arf_buffer != []:
            arf.reg_write(arf_buffer[0], arf_buffer[1])
            arf_buffer = []
        
        # CHECK CDB BUFFER
        if len(cdb_buffer) > 0:
            # update rs/rob
            #print "CDB UPDATE: " + cdb_buffer[0] + ", " + str(cdb_buffer[1])
            cdb_update(cdb_buffer[0], cdb_buffer[1])
            cdb_buffer = []
        
        # CHECK LS BUFFER
        for index, entry in enumerate(ls_buffer):
            if cycle_counter >= (entry["ready_cycle"]):
                available_ls_fu = available_ls_fu + 1
                # update lsq
                lsq.lsq_update_address(entry["destination"], entry["address"])
                #print "LSQ UPDATE ADDRESS: " + entry["destination"] + ", " + str(entry["address"])
                del ls_buffer[index]
                
        # UPDATE CDB USAGE
        if cdb_in_use == 1:
            cdb_in_use = 0
        
        # CHECK BRANCH BUFFER
        if branch_buffer != []:
            branch_buffer[1] = branch_buffer[1] -1
            if branch_buffer[1] == 0:# [branch resolution, ready_cycle, rob_entry]
                stall_instruction_buffer = 0
                if branch_buffer[0] == 1:
                    #set new PC
                    PC = int(rob.rob_get_destination(branch_buffer[2]))
                branch_buffer = []
                available_int_fu = available_int_fu + 1
                #print "INCREASE AVAILABLE INT FU"
         
        # CHECK INTEGER ADDER FUS AVAILABILITY
        if cycle_counter in int_adder_fu_timer:
            #increment available available_int_fu
            available_int_fu = available_int_fu + 1 
            #print "INCREASE AVAILABLE INT FU"
        
        #############################
        #PRINTINT EVERY CYCLE
        #############################
        #rob.rob_print()
        #rs.rs_print()
        #lsq.lsq_print()
        #timing_table.time_table_print()
        #memory.mem_print_non_zero_values()
        #arf.reg_print()
        #rat.rat_print()
        
        # print results and exit if rob is empty and instruction_buffer is exerted
        if (rob.rob_empty() == 1) and ((PC/4) >= len(instruction_buffer)) and (memory_is_in_use == 0):
            timing_table.time_table_print()
            arf.reg_print()
            memory.mem_print_non_zero_values()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
            break
        
        #print "-------------------------- CYCLE " + str(cycle_counter) + " --------------------------"
        #print "available_int_fu: " + str(available_int_fu)
        # SEPARATE FROM ROB
        
        #---------------------------------------------------------------------
        # ISSUE STAGE
        #---------------------------------------------------------------------
        # can_issue_new_instuction = (available_instuction_in_instruction_buffer) & (available_rob_entry) &  (available_rs_entry)
        rob_dest = "-" # signifies that an instruction wasn't issued on this cycle if stays to be "-"
        available_instuction_in_instruction_buffer = ((PC/4) < len(instruction_buffer))
        #print "available_instuction_in_instruction_buffer: " + str(available_instuction_in_instruction_buffer)
        available_rob_entry = (rob.rob_available() == 1)
        #print "available_rob_entry: " + str(available_rob_entry)
        if stall_instruction_buffer == 0 and available_instuction_in_instruction_buffer and available_rob_entry:
            # get insturction
            instruction = instruction_buffer[(PC/4)]
            #print "issued instruction: " + instruction
            instruction_parsed = instruction.split(" ")
            instruction_id = instruction_parsed[0]
            # check if there is an available rs entry based on instruction op       
            if instruction_id in ["ADD", "ADDI", "SUB", "BEQ", "BNE"]: # check int_adder_rs
                available_rs_entry = (rs.rs_available("int_adder_rs") != -1)
                if available_rs_entry:
                    # add entry
                    # check if we have values of qj and qk
                    if instruction_id in ["BEQ", "BNE"]:
                        # handle branch instructions
                        stall_instruction_buffer = 1 # stall issuing instructions temporarily until branch is resolved
                        reg1 = get_current_reg_info(instruction_parsed[1]) # reg_name
                        reg2 = get_current_reg_info(instruction_parsed[2]) # reg_name
                        branch_dest = PC + 4 + int(instruction_parsed[3])*4 #PC+4+offset<<2
                        rob_dest = rob.rob_instr_add(instruction, branch_dest, timing_table_entry_index)
                        # RAT doesn't need updating for branch: rat.int_rat_update(instruction_parsed[1], rob_dest) # need to update rat
                    else:
                        reg1 = get_current_reg_info(instruction_parsed[2]) # reg_name
                        if instruction_id in ["ADDI"]:
                            reg2 = [int(instruction_parsed[3]), "-"]
                        else:
                            reg2 = get_current_reg_info(instruction_parsed[3]) # reg_name
                        rob_dest = rob.rob_instr_add(instruction, instruction_parsed[1], timing_table_entry_index)
                        rat.int_rat_update(instruction_parsed[1], rob_dest) # need to update rat
                    timing_table_entry_index = timing_table_entry_index + 1
                    rs.rs_add("int_adder_rs", instruction_id, rob_dest, reg1[0], reg2[0], reg1[1], reg2[1]) # rs_name, i, op, dest, vj, vk, qj, qk
                    timing_table.timing_table_add(PC, instruction, cycle_counter)
                    PC = PC + 4
            elif instruction_id in ["ADD.D", "SUB.D"]: # check fp_adder_rs
                available_rs_entry = (rs.rs_available("fp_adder_rs") != -1)
                if available_rs_entry:
                    # add entry
                    # check if we have values of qj and qk
                    reg1 = get_current_reg_info(instruction_parsed[2]) # reg_name
                    reg2 = get_current_reg_info(instruction_parsed[3]) # reg_name
                    rob_dest = rob.rob_instr_add(instruction, instruction_parsed[1], timing_table_entry_index)
                    rat.fp_rat_update(instruction_parsed[1], rob_dest) # need to update rat
                    timing_table_entry_index = timing_table_entry_index + 1
                    rs.rs_add("fp_adder_rs", instruction_id, rob_dest, reg1[0], reg2[0], reg1[1], reg2[1]) # rs_name, i, op, dest, vj, vk, qj, qk
                    timing_table.timing_table_add(PC, instruction, cycle_counter)
                    PC = PC + 4
            elif instruction_id in ["MULT.D"]: # check fp_multiplier_rs
                available_rs_entry = (rs.rs_available("fp_multiplier_rs") != -1)
                if available_rs_entry:
                    # add entry
                    #check if we have values of qj and qk
                    reg1 = get_current_reg_info(instruction_parsed[2]) # reg_name
                    reg2 = get_current_reg_info(instruction_parsed[3]) # reg_name
                    rob_dest = rob.rob_instr_add(instruction, instruction_parsed[1], timing_table_entry_index)
                    rat.fp_rat_update(instruction_parsed[1], rob_dest) # need to update rat
                    timing_table_entry_index = timing_table_entry_index + 1
                    rs.rs_add("fp_multiplier_rs", instruction_id, rob_dest, reg1[0], reg2[0], reg1[1], reg2[1]) # rs_name, i, op, dest, vj, vk, qj, qk
                    timing_table.timing_table_add(PC, instruction, cycle_counter)
                    PC = PC + 4
            elif instruction_id in ["SD"]:
                available_rs_entry = (lsq.lsq_available() != -1)
                if available_rs_entry:
                    # add entry
                    #check if we have the needed values
                    addr_reg = get_current_reg_info(instruction_parsed[2].split("(")[1].split(")")[0]) # reg_name
                    constant = instruction_parsed[2].split("(")[0]
                    #specific to SD
                    source_reg = get_current_reg_info(instruction_parsed[1]) # only needed for store instructions
                    rob_dest = rob.rob_instr_add(instruction, "-", timing_table_entry_index)
                    timing_table_entry_index = timing_table_entry_index + 1
                    #no need to update rat since we are only storing a value to memory (not bringing anything back)
                    #add entry to lsq
                    lsq.lsq_add(instruction_id, constant, addr_reg[0], addr_reg[1], source_reg[0], source_reg[1], rob_dest)
                    timing_table.timing_table_add(PC, instruction, cycle_counter)
                    PC = PC + 4
            elif instruction_id in ["LD"]:
                available_rs_entry = (lsq.lsq_available() != -1)
                if available_rs_entry:
                    # add entry
                    #check if we have the needed values
                    addr_reg = get_current_reg_info(instruction_parsed[2].split("(")[1].split(")")[0]) # reg_name
                    constant = instruction_parsed[2].split("(")[0]
                    #specific to SD
                    source_reg = ["-", "-"]
                    rob_dest = rob.rob_instr_add(instruction, instruction_parsed[1], timing_table_entry_index)
                    timing_table_entry_index = timing_table_entry_index + 1
                    #update rat
                    rat.rat_update(instruction_parsed[1], rob_dest) # need to update rat
                    #add entry to lsq
                    lsq.lsq_add(instruction_id, constant, addr_reg[0], addr_reg[1], source_reg[0], source_reg[1], rob_dest)
                    timing_table.timing_table_add(PC, instruction, cycle_counter)
                    PC = PC + 4
            else:
                print "Invalid instruction!"
                exit(1)
 
        # cycle through ROB
        # check what to do with instructions that are in ISSUE/EX/MEM stages
        rob_entry = rob.rob_head_node(rob_dest) 
        while rob_entry != -1:
            #print "-- checking rob entry " + rob_entry + " --"
            rob_entry_state = rob.rob_get_state(rob_entry)
            rob_entry_instruction_id = rob.rob_get_instruction_id(rob_entry)
            if rob_entry_state == "MEM":
                #---------------------------------------------------------------------
                # MEM -> WB
                #---------------------------------------------------------------------
                #can_move_from_mem_to_wb_stage = (forwarding_flag_set) & ((cycle_counter-mem_s) == 1)  & (!cdb_will_be_in_use_next_cycle) or (!forwarding_flag_set) & ((cycle_counter-mem_s) == fu_mem_cycles) & (!cdb_will_be_in_use_next_cycle)
                mem_stage_done = (timing_table.timing_table_check_if_done(rob.rob_get_tt_index(rob_entry), "MEM", cycle_counter) == 1)
                if mem_stage_done and cdb_in_use == 0:
                    # when mem stage done and cdb available -> cast loaded value on cdb to rob
                    cdb_in_use = 1
                    if lsq.lsq_fwd_flag_set(rob_entry) == 1:
                        result = lsq.lsq_get_fwd_value(rob_entry)
                    else:
                        #write loaded value to a list of values loaded from memory
                        result = memory.mem_read(lsq.lsq_get_address(rob_entry))
                    #dequeue lsq
                    lsq.lsq_dequeue(rob_entry) #MAY BE A PROBLEM (CHECK LATER - MAY NEED TO DO THIS BEFORE CYCLING THROUGH ROB) !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!                    
                    # add result to cdb buffer                        
                    cdb_buffer = [rob_entry, result]    
                    # update rob state
                    rob.rob_update_state(rob_entry, "WB")
                    # update timing table
                    #print "WB FOR " + rob_entry + ": " + str(cycle_counter)
                    timing_table.timing_table_update(rob.rob_get_tt_index(rob_entry), "WB", cycle_counter, 1)                    
            elif rob_entry_state == "EX" and rob_entry_instruction_id == "LD":  
                #---------------------------------------------------------------------
                # EX -> MEM
                #---------------------------------------------------------------------
                #can_move_from_ex_to_mem_stage = (ld_instuction) & ((cycle_counter-ex_s) == fu_execution_cycles) & (!memory_will_be_in_use_next_cycle)
                ex_stage_done = (timing_table.timing_table_check_if_done(rob.rob_get_tt_index(rob_entry), "EX", cycle_counter) == 1)
                if ex_stage_done:
                    forwarding_happened = (lsq.lsq_forwarding(rob_entry) != -1)
                    if forwarding_happened:
                        #update timing table
                        #print "MEM FOR " + rob_entry + ": LD STARTS IN CYCLE " + str(cycle_counter) + " AND ENDS IN CYCLE " + str(cycle_counter)
                        timing_table.timing_table_update(rob.rob_get_tt_index(rob_entry), "MEM", cycle_counter, 1)
                        #update rob
                        rob.rob_update_state(rob_entry, "MEM")
                    elif memory_is_in_use == 0:
                        #update timing table
                        memory_is_in_use = load_store_unit_properties["cycles_in_mem"]
                        #print "MEM FOR " + rob_entry + ": LD STARTS IN CYCLE " + str(cycle_counter) + " AND ENDS IN CYCLE " + str(cycle_counter + load_store_unit_properties["cycles_in_mem"]-1)
                        timing_table.timing_table_update(rob.rob_get_tt_index(rob_entry), "MEM", cycle_counter, load_store_unit_properties["cycles_in_mem"])
                        #update rob
                        rob.rob_update_state(rob_entry, "MEM")                        
            elif rob_entry_state == "EX": # not ld instruction   
                #---------------------------------------------------------------------
                # EX -> WB STAGE
                #---------------------------------------------------------------------            
                #can_move_from_ex_to_wb_stage = (!ld_instuction) & ((cycle_counter-ex_s) == fu_execution_cycles) & (!cdb_will_be_in_use_next_cycle)
                ex_stage_done = (timing_table.timing_table_check_if_done(rob.rob_get_tt_index(rob_entry), "EX", cycle_counter) == 1)
                if ex_stage_done and rob_entry_instruction_id in ["BEQ", "BNE"]:
                    # clear rs entry
                    rs.rs_clear_entry(rob_entry)
                    # update rob state
                    rob.rob_update_state(rob_entry, "WB")
                    # update rob and set busy to no
                    rob.rob_update_value(rob_entry, "-")
                    # update timing table
                    #print "WB FOR " + rob_entry + ": " + str(cycle_counter)
                    timing_table.timing_table_update(rob.rob_get_tt_index(rob_entry), "WB", cycle_counter, 1)
                elif ex_stage_done and cdb_in_use == 0:
                    # move to wb stage                
                    if rob_entry_instruction_id in ["ADD", "ADDI", "SUB", "ADD.D", "SUB.D", "MULT.D"]:
                        # normal writeback procedure
                        cdb_in_use = 1
                        # write to cdb buffer
                        if rob_entry_instruction_id in ["ADD", "ADDI"]:
                            # perform addition
                            values = rs.rs_get_values("int_adder_rs", rob_entry)
                            result = values[0] + values[1]
                            # add result to cdb buffer                        
                            cdb_buffer = [rob_entry, result]
                        elif rob_entry_instruction_id in ["SUB"]:
                            # perform subtraction
                            values = rs.rs_get_values("int_adder_rs", rob_entry)
                            result = values[0] - values[1]
                            # add result to cdb buffer
                            cdb_buffer = [rob_entry, result]
                        elif rob_entry_instruction_id == "ADD.D":
                            # perform addition
                            values = rs.rs_get_values("fp_adder_rs", rob_entry)
                            result = float(values[0] + values[1])
                            # add result to cdb buffer
                            cdb_buffer = [rob_entry, result]
                        elif rob_entry_instruction_id == "SUB.D":
                            # perform addition
                            values = rs.rs_get_values("fp_adder_rs", rob_entry)
                            result = float(values[0] - values[1])
                            # add result to cdb buffer
                            cdb_buffer = [rob_entry, result]
                        elif rob_entry_instruction_id == "MULT.D":
                            # perform multiplication
                            values = rs.rs_get_values("fp_multiplier_rs", rob_entry)
                            result = float(values[0]*values[1])
                            # add result to cdb buffer
                            cdb_buffer = [rob_entry, result]
                        # clear rs entry
                        rs.rs_clear_entry(rob_entry)
                        # update rob state
                        rob.rob_update_state(rob_entry, "WB")
                        # update timing table
                        #print "WB FOR " + rob_entry + ": " + str(cycle_counter)
                        timing_table.timing_table_update(rob.rob_get_tt_index(rob_entry), "WB", cycle_counter, 1)
                    elif rob_entry_instruction_id in ["SD"]:
                        #when value is available -> write value (source) field to rob
                        if lsq.lsq_store_val_available(rob_entry) != -1:
                            # normal writeback procedure
                            cdb_in_use = 1
                            # add value to cdb buffer
                            cdb_buffer = [rob_entry, lsq.lsq_get_store_val(rob_entry)]                                               
                            # update rob state
                            rob.rob_update_state(rob_entry, "WB")
                            # update timing table
                            #print "WB FOR " + rob_entry + ": " + str(cycle_counter)
                            timing_table.timing_table_update(rob.rob_get_tt_index(rob_entry), "WB", cycle_counter, 1)                
            elif rob_entry_state == "ISSUE":    
                #---------------------------------------------------------------------
                # ISSUE -> EX
                #---------------------------------------------------------------------            
                #can_move_to_ex_stage = (alu_int_instruction) & (no_register_dependencies) & (available_int_fu) or (!alu_int_instruction) & (no_register_dependencies)
                if rob_entry_instruction_id in ["ADD", "ADDI"]:
                    # find rs entry (by using ROB entry name)
                    no_dependencies = (rs.rs_no_dependencies("int_adder_rs", rob_entry) != -1)
                    if no_dependencies and available_int_fu != 0:
                        # decrement available_int_fu
                        available_int_fu = available_int_fu - 1
                        #print "DECREASE AVAILABLE INT FU " + str(available_int_fu)
                        #update stage info in rob
                        rob.rob_update_state(rob_entry, "EX")
                        #update stage infor in tt
                        #print "EX FOR " + rob_entry + ": ADD/ADDI STARTS IN CYCLE " + str(cycle_counter) + " AND ENDS IN CYCLE " + str(cycle_counter + int_adder_properties["cycles_in_ex"]-1)
                        timing_table.timing_table_update(rob.rob_get_tt_index(rob_entry), "EX", cycle_counter, int_adder_properties["cycles_in_ex"])
                        #add a timer for int adder instruction unit
                        int_adder_fu_timer.append(cycle_counter + int_adder_properties["cycles_in_ex"])
                elif rob_entry_instruction_id in ["SUB"]:
					# find rs entry (by using ROB entry name)
                    no_dependencies = (rs.rs_no_dependencies("int_adder_rs", rob_entry) != -1)
                    if no_dependencies and available_int_fu != 0:
						# decrement available_int_fu
                        available_int_fu = available_int_fu - 1
                        #print "DECREASE AVAILABLE INT FU: " + str(available_int_fu)
                        #update stage info in rob
                        rob.rob_update_state(rob_entry, "EX")
                        #update stage infor in tt
                        #print "EX FOR " + rob_entry + ": SUB STARTS IN CYCLE " + str(cycle_counter) + " AND ENDS IN CYCLE " + str(cycle_counter + int_adder_properties["cycles_in_ex"]-1)
                        timing_table.timing_table_update(rob.rob_get_tt_index(rob_entry), "EX", cycle_counter, int_adder_properties["cycles_in_ex"])
                        int_adder_fu_timer.append(cycle_counter + int_adder_properties["cycles_in_ex"])
                elif rob_entry_instruction_id == "ADD.D":
					# find rs entry (by using ROB entry name)
                    no_dependencies = (rs.rs_no_dependencies("fp_adder_rs", rob_entry) != -1)
                    if no_dependencies and available_fp_adder_fu != 0:
						# decrement available_fp_adder_fu
                        available_fp_adder_fu = available_fp_adder_fu - 1
                        #update stage info in rob
                        rob.rob_update_state(rob_entry, "EX")
                        #update stage infor in tt
                        #print "EX FOR " + rob_entry + ": ADD.D STARTS IN CYCLE " + str(cycle_counter) + " AND ENDS IN CYCLE " + str(cycle_counter + fp_adder_properties["cycles_in_ex"]-1)
                        timing_table.timing_table_update(rob.rob_get_tt_index(rob_entry), "EX", cycle_counter, fp_adder_properties["cycles_in_ex"])
                elif rob_entry_instruction_id == "SUB.D":
					# find rs entry (by using ROB entry name)
                    no_dependencies = (rs.rs_no_dependencies("fp_adder_rs", rob_entry) != -1)
                    if no_dependencies and available_fp_adder_fu != 0:
						# decrement available_fp_adder_fu
                        available_fp_adder_fu = available_fp_adder_fu - 1
                        #update stage info in rob
                        rob.rob_update_state(rob_entry, "EX")
                        #update stage infor in tt
                        #print "EX FOR " + rob_entry + ": SUB.D STARTS IN CYCLE " + str(cycle_counter) + " AND ENDS IN CYCLE " + str(cycle_counter + fp_adder_properties["cycles_in_ex"]-1)
                        timing_table.timing_table_update(rob.rob_get_tt_index(rob_entry), "EX", cycle_counter, fp_adder_properties["cycles_in_ex"])
                elif rob_entry_instruction_id == "MULT.D":
					# find rs entry (by using ROB entry name)
                    no_dependencies = (rs.rs_no_dependencies("fp_multiplier_rs", rob_entry) != -1)
                    if no_dependencies and available_fp_mult_fu != 0:
						# decrement available_fp_mult_fu
                        available_fp_mult_fu = available_fp_mult_fu - 1
                        #update stage info in rob
                        rob.rob_update_state(rob_entry, "EX")
                        #update stage infor in tt
                        #print "EX FOR " + rob_entry + ": SUB.D STARTS IN CYCLE " + str(cycle_counter) + " AND ENDS IN CYCLE " + str(cycle_counter + fp_multiplier_properties["cycles_in_ex"]-1)
                        timing_table.timing_table_update(rob.rob_get_tt_index(rob_entry), "EX", cycle_counter, fp_multiplier_properties["cycles_in_ex"])
                elif rob_entry_instruction_id in ["BEQ", "BNE"]: # resolve branch using int adder
					# find rs entry (by using ROB entry name)
                    no_dependencies = (rs.rs_no_dependencies("int_adder_rs", rob_entry) != -1)
                    if no_dependencies and available_int_fu != 0:
						# decrement available_int_fu
                        available_int_fu = available_int_fu - 1   
                        #print "DECREASE AVAILABLE INT FU " + str(available_int_fu)
                        #resolve branch
                        values = rs.rs_get_values("int_adder_rs", rob_entry)
                        if rob_entry_instruction_id == "BEQ":
                            branch_buffer = [(values[0] == values[1]), int_adder_properties["cycles_in_ex"], rob_entry] # resolution, ready_cycle, rob_entry
                            #print "Branch formula: " + str(values[0]) + " == " + str(values[1])
                        elif rob_entry_instruction_id == "BNE":
                            branch_buffer = [(values[0] != values[1]), int_adder_properties["cycles_in_ex"], rob_entry] # resolution, ready_cycle, rob_entry     
                            #print "Branch formula: " + str(values[0]) + " != " + str(values[1])
                        #update stage info in rob
                        rob.rob_update_state(rob_entry, "EX")
                        #update stage infor in tt
                        timing_table.timing_table_update(rob.rob_get_tt_index(rob_entry), "EX", cycle_counter, int_adder_properties["cycles_in_ex"])
                elif instruction_id in ["SD", "LD"]: # calculate address
                    no_dependencies = (lsq.lsq_addr_reg_ready(rob_entry) != -1)
                    if no_dependencies and available_ls_fu != 0:
                        # decrement available_ls_fu
                        available_ls_fu = available_ls_fu - 1
						# calculate address
                        values = lsq.lsq_get_address_values(rob_entry)
                        #print "LSQ values: " + str(values)
                        ls_address = int(values[0])*4 + int(values[1])
                        # add calculated address to ls_buffer that will update lsq as soon as execution time is done
                        ls_buffer.append({"destination" : rob_entry, "address" : ls_address, "ready_cycle" : cycle_counter + load_store_unit_properties["cycles_in_ex"]}.copy())
                        # update ROB entry destination
                        rob.rob_update_sd_destination(rob_entry, ls_address)
                        #update stage info in rob
                        rob.rob_update_state(rob_entry, "EX")
                        #update stage infor in tt
                        #print "EX FOR " + rob_entry + ": L/S STARTS IN CYCLE " + str(cycle_counter) + " AND ENDS IN CYCLE " + str(cycle_counter + load_store_unit_properties["cycles_in_ex"]-1)
                        timing_table.timing_table_update(rob.rob_get_tt_index(rob_entry), "EX", cycle_counter, load_store_unit_properties["cycles_in_ex"])
                        
            rob_entry = rob.rob_next(rob_entry, rob_dest) # get next rob entry
        
        #---------------------------------------------------------------------
        # WB -> COMMIT STAGE
        #---------------------------------------------------------------------
        #can_move_from_wb_to_commit = (!commit_in_use) & (rob_top_instruction_ready_to_commit)
        rob_entry_data = rob.rob_check_if_ready_to_commit() # [tt_index, destination, value, instruction_id, rob_entry_name]
        if rob_entry_data != -1:
            if rob_entry_data[3] in ["ADD", "ADDI", "SUB", "ADD.D", "SUB.D", "MULT.D", "LD"]: 
                #clear rob entry
                rob.rob_commit() # [tt_index, destination, value, instruction_id, rob_entry_name]
                cycles_in_commit = 1
                #set arf buffer
                arf_buffer = [rob_entry_data[1], rob_entry_data[2]] # [destination, value]
                #if rat still points to this ROB entry -> clean it up
                if rat.rat_get(rob_entry_data[1]) == rob_entry_data[4]:
                    rat.rat_update(rob_entry_data[1], rob_entry_data[1])
                #update timing table
                timing_table.timing_table_update(rob_entry_data[0], "COMMIT", cycle_counter, cycles_in_commit)    
                #print "COMMIT FOR " + rob_entry_data[4] + ": STARTS IN CYCLE " + str(cycle_counter) + " AND ENDS IN CYCLE " + str(cycle_counter + cycles_in_commit - 1)
            elif rob_entry_data[3] == "SD" and memory_is_in_use == 0:
                #clear rob entry
                rob.rob_commit() # [tt_index, destination, value, instruction_id, rob_entry_name]
                cycles_in_commit = 1
                #set memory_buffer
                memory_buffer = [rob_entry_data[1], rob_entry_data[2], rob_entry_data[4]] # [destination, value, rob_entry]
                cycles_in_commit = load_store_unit_properties["cycles_in_mem"]
                #set memory in use
                memory_is_in_use = load_store_unit_properties["cycles_in_mem"]                
                #update timing table
                timing_table.timing_table_update(rob_entry_data[0], "COMMIT", cycle_counter, cycles_in_commit)    
                #print "COMMIT FOR " + rob_entry_data[4] + ": STARTS IN CYCLE " + str(cycle_counter) + " AND ENDS IN CYCLE " + str(cycle_counter + cycles_in_commit - 1)        
            elif rob_entry_data[3] in ["BEQ", "BNE"]:
                #clear rob entry
                rob.rob_commit() # [tt_index, destination, value, instruction_id, rob_entry_name]
                cycles_in_commit = 1
                #update timing table
                timing_table.timing_table_update(rob_entry_data[0], "COMMIT", cycle_counter, cycles_in_commit)    
                #print "COMMIT FOR " + rob_entry_data[4] + ": STARTS IN CYCLE " + str(cycle_counter) + " AND ENDS IN CYCLE " + str(cycle_counter + cycles_in_commit - 1)
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
            print "###############################################################################################################################################################"
            print "{:^159}".format("INTEGER ADDER PROPERTIES")
            print "###############################################################################################################################################################"
            print "Number of reservation stations: " + str(int_adder_properties["num_rs"])
            print "Number of cycles in execution stage: " + str(int_adder_properties["cycles_in_ex"])
            print "Number of function Units: " + str(int_adder_properties["num_fus"])
        elif(line[0] == "FP_ADDER"):
            # set fp_adder_properties
            fp_adder_properties["num_rs"] = int(line[1])
            fp_adder_properties["cycles_in_ex"] = int(line[2])
            fp_adder_properties["num_fus"] = int(line[3])
            print "###############################################################################################################################################################"
            print "{:^159}".format("FP ADDER PROPERTIES")
            print "###############################################################################################################################################################"
            print "Number of reservation stations: " + str(int_adder_properties["num_rs"])
            print "Number of cycles in execution stage: " + str(int_adder_properties["cycles_in_ex"])
            print "Number of function Units: " + str(int_adder_properties["num_fus"])
        elif(line[0] == "FP_MULTIPLIER"):
            # set fp_multiplier_properties
            fp_multiplier_properties["num_rs"] = int(line[1])
            fp_multiplier_properties["cycles_in_ex"] = int(line[2])
            fp_multiplier_properties["num_fus"] = int(line[3])
            print "###############################################################################################################################################################"
            print "{:^159}".format("FP MULTIPLIER PROPERTIES")
            print "###############################################################################################################################################################"
            print "Number of reservation stations: " + str(fp_multiplier_properties["num_rs"])
            print "Number of cycles in execution stage: " + str(fp_multiplier_properties["cycles_in_ex"])
            print "Number of function Units: " + str(fp_multiplier_properties["num_fus"])
        elif(line[0] == "LOAD_STORE_UNIT"):
            # set load_store_unit_properties
            load_store_unit_properties["num_rs"] = int(line[1])
            load_store_unit_properties["cycles_in_ex"] = int(line[2])
            load_store_unit_properties["cycles_in_mem"] = int(line[3])
            load_store_unit_properties["num_fus"] = int(line[4])
            print "###############################################################################################################################################################"
            print "{:^159}".format("LOAD STORE UNIT PROPERTIES")
            print "###############################################################################################################################################################"
            print "Number of reservation stations: " + str(load_store_unit_properties["num_rs"])
            print "Number of cycles in execution stage: " + str(load_store_unit_properties["cycles_in_ex"])
            print "Number of cycles in memory stage: " + str(load_store_unit_properties["cycles_in_mem"])
            print "Number of function Units: " + str(load_store_unit_properties["num_fus"])
        elif(line[0] == "ROB_ENTRIES"):
            # set num_rob_entries
            num_rob_entries = int(line[1])
            print "###############################################################################################################################################################"
            print "{:^159}".format("ROB PROPERTIES")
            print "###############################################################################################################################################################"
            print "Number of rob entries: " + str(num_rob_entries)
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
        
def cdb_update(destination, value):
    # when value is ready in RS -> broadcast values to ROB, RS
    # other situations
    
    # check and update rs
    rs.rs_update_value(destination, value)
  
    # check and update load store queue
    lsq.lsq_update_value(destination, value)
    
    # check and update rob
    rob.rob_update_value(destination, value)
############################################################################################################

if __name__ == "__main__":
    if len(argv) > 1:
        main(argv[1]) # python2.7 tomasulo_main.py input_file.txt
    else:
        print "Please specify input file!"
        exit(1)