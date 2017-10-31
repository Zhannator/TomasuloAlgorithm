#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

# Global Variables
memory = [] # needs to be initialized, 256B(64W), needs its own function on how to reference locations in mem by word/byte

############################################################################################################
# MEMORY MANAGEMENT
############################################################################################################		
def memory_initialize():
    # code to initialize memory
    print ("test")

def memory_store_at_addr(addr, value):
	# code to store value at addr
    print ("test")
    
def memory_load_from_addr(addr):
	# code to load from addr
    print ("test")
############################################################################################################

if __name__ == "__main__":
    memory_initialize()
    memory_store_at_addr(32, 100) # store 100 at address 32
    memory_load_from_addr(32) # load 100 from address 32