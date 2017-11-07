#!/usr/bin/python
# -*- coding: utf-8 -*-

# Tomasulo MEMORY

class MEMobject:	
    def mem_initialize(self):
        # code to initialize memory
        self.memory = [0]*64 # 265B (64W)

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