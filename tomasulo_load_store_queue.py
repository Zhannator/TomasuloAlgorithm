
#!/usr/bin/python
# -*- coding: utf-8 -*-

# Tomasulo Load-Store Queue 

load_store_queue = []

def load_store_queue_add(load_store, load_store_pc, load_store_seq, load_store_addr, load_store_value):
    #add an entry in the queue if its not full

    if len(load_store_queue) < num_load_store_rs:
        load_store_queue_entry = { 
            "l/s" : "-",
            "pc" : "-",
            "seq" : "-",
            "addr" : 0,
            "value" : 0 }
        load_store_queue.append(load_store_queue_entry.copy())
        
        #update the fields
        load_store_queue[0]["l/s"] = load_store
        load_store_queue[0]["pc"] = load_store_pc
        load_store_queue[0]["seq"] = load_store_seq
        load_store_queue[0]["addr"] = load_store_addr
        load_store_queue[0]["value"] = load_store_value
    
    else:
        print "load-store queue full!"
        return -1
 
 
load_store_queue_pop():
    #pop the oldest instruction from the queue once it completes
    
    load_store_queue.pop()

def load_store_queue_update(load_store_value, load_store_index):
    #load_store_value  -> update value or address if it changes
    #load_store_index  -> index for which row to update in the queue
    
    load_store_queue[load_store_index]["value"] = load_store_value
    
    
if __name__ == "__main__":
    main()        

