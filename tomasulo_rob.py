#!/usr/bin/python
# -*- coding: utf-8 -*-

# Tomasulo ROB

rob = []

instruction_buffer = ["Add.d R1 R2 R3", "Add.d R2 R2 R3", "Add.d R3 R2 R3", "Add.d R4 R2 R3", "Add.d R5 R2 R3"]
rob_check_counter = 0
rob_add_counter = 0
rob_update_index = 0
rob_done_counter = num_rob_entries


##########################################################
# MAIN
##########################################################

def main():
	
	rob_initialize()
	
	for instruction in instruction_buffer:
		dest = instruction.split()[1]
		rob_instr_add(dest)
	
	rob_check()
		
##########################################################
def rob_initialize():
    # initialize rob
    global rob
    rob_entry = { # needs to be initialized
	"busy" : "-",
    "instruction" : "-",
    "state" : "-",
    "destination" : "-", # “dest" field of a store instruction records its location in the load/store queue
    "value" : "-"
    }
    
    for i in range(num_rob_entries):
        rob.append(rob_entry.copy())
    
    
def rob_instr_add(rob_dest):
	#add entry after you fetch instruction
    global rob_add_counter
    global num_rob_entries
    
    if rob_add_counter <= num_rob_entries:
        rob[rob_add_counter]["destination"] = rob_dest
        rob_add_counter = rob_add_counter + 1; 
    else:
        print "ROB full!"
        return -1
    print rob
    print
	
def rob_check():
	#use busy flag to check if any entries are ready 
	#use counter for position in rob
	
	global rob_check_counter
        
    if rob[rob_check_counter]["busy"] == "no":
        print "rob" + str(rob_check_counter) + "is ready"
    
    if rob_check_counter == num_rob_entries:
        rob_check_counter = 0
    else:
        rob_check_counter = rob_check_counter + 1
        
        
def rob_update_value(dest_tag, rs_value):
	#use reservation stations to update rob when instructions have completed
    
    rob_update_index = int(dest_tab.split("ROB")[1])
    
    rob[rob_update_index]["value"] = rs_value
	
	
	
	
	
	
if __name__ == "__main__":
    main()