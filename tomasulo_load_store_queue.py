
#!/usr/bin/python
# -*- coding: utf-8 -*-

# Tomasulo Load-Store Queue 

load_store_queue = []

def load_store_queue_add(.....):

    if len(load_store_queue) < num_load_store_rs:
        load_store_queue_entry = { 
            "l/s" : "-",
            "pc" : "-",
            "seq" : "-",
            "addr" : 0,
            "value" : 0 }
        load_store_queue.append(load_store_queue_entry.copy())
    else:
        print "load-store queue full!"
        return -1
    

def load_store_queue_update(load_store_instr, num_load_store_rs):
    #Must be performed in order
    #load_store_instr  -> string for the instruction that was fetched
    #num_load_store_rs -> number of reservation stations for load-store queue
    
    load_store_queue[load_store_index]["l/s"] = load_store_instr
    load_store_index = load_store_index + 1
    
    
        

