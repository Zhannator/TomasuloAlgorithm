#!/usr/bin/python
# -*- coding: utf-8 -*-

# Tomasulo MEMORY

class MEMobject:	
    memory = []
    
    def mem_initialize(self):
        # code to initialize memory
        self.memory = [0]*64 # 256B (64W)

    def mem_write(self, addr, value):
        # code to store value at addr
        # addr, value are strings
        # addr must be specified in byte
        self.memory[int(int(addr)/4)] = float(value)
        
    def mem_read(self, addr):
        # code to load from addr
        # addr is string
        # addr must be specified in byte
        return self.memory[int(int(addr)/4)]
        
    def mem_print(self):
        print "###############################################################################################################################################################"
        print "{:^159}".format("MEMORY")
        print "###############################################################################################################################################################"
        row_format ="{:^10}" * 16
        print row_format.format(*self.memory[0:16])
        print row_format.format(*self.memory[16:32])
        print row_format.format(*self.memory[32:48])
        print row_format.format(*self.memory[48:64])
        print
        
    def mem_print_non_zero_values(self):
        print "###############################################################################################################################################################"
        print "{:^159}".format("NON-ZERO MEMORY VALUES")
        print "###############################################################################################################################################################"
        row_format ="{:^10}" * 2
        print row_format.format(*["ADDRESS", "VALUE"])
        for address, word in enumerate(self.memory):
            if word != 0:
                print row_format.format(*["0x%x" % (address*4), word])
        print