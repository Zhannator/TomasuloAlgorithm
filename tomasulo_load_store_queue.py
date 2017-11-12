
#!/usr/bin/python
# -*- coding: utf-8 -*-

# Tomasulo Load-Store Queue 

load_store_queue = []

def load_store_queue_add(load_store_instr, load_store_value, load_store_valueDepend):
    #add an entry in the queue if its not full:
    #    1) LOAD  -> addr (until EX stage) and value (until MEM stage unless forwarding) are NOT ready
    #    2) STORE -> addr (until EX stage) is NOT ready, value readiness depends on data dependencies
    #when a LOAD entry is added, run through queue to see if older STORE instr (with same addr) will forward
    #   -> which earlier STORE do I get my value from?

    if len(load_store_queue) < num_load_store_rs:
        load_store_queue_entry = { 
            "l/s" : "-",    #Load or Store instruction
            "V_j" : "-",    #Value
            "Q_j" : "-",    #Value dependency for V_j
            "V_k" : "-",    #Address
            "Q_k" : "-",    #Address dependency for V_k
            "FWD" : "-"}    #Set flag if forwarding used 
        load_store_queue.append(load_store_queue_entry.copy())
        
        #update the fields
        load_store_queue[0]["l/s"] = load_store_instr
        load_store_queue[0]["V_j"] = load_store_value
        load_store_queue[0]["Q_j"] = load_store_valueDepend
        
    
    else:
        print "load-store queue full!"
        return -1
    
    if load_store_queue["l/s"] == "LD"
        #Call this function to check if we can forward value from a STORE instr 
        #to this added entry (if LOAD instr)
        load_store_queue_forwarding(1)

########################################################################## 
def load_store_queue_pop():
    #pop the oldest instruction from the queue once it completes
    
    load_store_queue.pop()

##########################################################################
def load_store_queue_update_addr(load_store_addr, load_store_index):
    #load_store_value  -> update address if it changes
    #load_store_index  -> index for which row to update in the queue
    #when an entry is updated, also need to perform Store-to-load forwarding
    
    load_store_queue[load_store_index]["V_k"] = load_store_addr
    load_store_queue[load_store_index]["Q_k"] = "-"     #once the addr is updated, there is no more dependency
    
##########################################################################    
def load_store_queue_update_value(load_store_value, load_store_index):
    #load_store_value  -> update address if it changes
    #load_store_index  -> index for which row to update in the queue
    #when an entry is updated, also need to perform Store-to-load forwarding
    
    load_store_queue[load_store_index]["V_j"] = load_store_value
    load_store_queue[load_store_index]["Q_j"] = "-"     #once the value is updated, there is no more dependency

##########################################################################    
def load_store_queue_read():
    #read the oldest value in the queue
    #when load  -> pop to ROB
    #when store -> queue has to wait
    
    
##########################################################################    
def load_store_queue_forwarding(flag):
    #forward happens
    #flag -> 0 means forward after queue update
    #flag -> 1 means forward after queue add
    
    
if __name__ == "__main__":
    main()        

