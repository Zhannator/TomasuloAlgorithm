#!/usr/bin/python
# -*- coding: utf-8 -*-

# Tomasulo ARF
class ARFobject:
    int_registers = [] # 32 registers by DLX standard
    fp_registers = [] # 32 registers by DLX standard
    
    def reg_initialize(self):
        # code to initialize memory
        self.int_registers = [0]*32
        self.fp_registers = [0]*32

    def reg_write(self, register, value):
        # code to store value at addr
        # register, value are strings
        if register[0] == 'R':
            reg_num = int(register.split('R')[1])
            if reg_num < 32 and reg_num != 0:
                self.int_registers[reg_num] = int(value)
            else:
                print "Invalid register!"
                exit(0)
        elif register[0] == 'F':
            reg_num = int(register.split('F')[1])
            if reg_num < 32:
                self.fp_registers[reg_num] = float(value)
            else:
                print "Invalid register!"
                exit(0)
        else:
            print ("Invalid register!")
            exit(0)
        
    def reg_read(self, register):
        # code to load from addr
        # register is string
        if register[0] == 'R':
            reg_num = int(register.split('R')[1])
            if reg_num < 32:
                return self.int_registers[reg_num]
            else:
                print "Invalid register!"
                exit(0)
        elif register[0] == 'F':
            reg_num = int(register.split('F')[1])
            if reg_num < 32:
                return self.fp_registers[reg_num]
            else:
                print "Invalid register!"
                exit(0)
        else:
            print ("Invalid register!")
            exit(0)