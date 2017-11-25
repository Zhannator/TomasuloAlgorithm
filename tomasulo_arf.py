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

    def reg_print(self):
        print "###############################################################################################################################################################"
        print "{:^159}".format("INTEGER ARF")
        print "###############################################################################################################################################################"    
        row_format ="{:^10}" * 16
        reg_names = ["R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11", "R12", "R13", "R14", "R15"]
        print row_format.format(*reg_names)
        print row_format.format(*self.int_registers[0:16])
        reg_names = ["R16", "R17", "R18", "R19", "R20", "R21", "R22", "R23", "R24", "R25", "R26", "R27", "R28", "R29", "R30", "R31"]
        print row_format.format(*reg_names)
        print row_format.format(*self.int_registers[16:32])
        print
        print "###############################################################################################################################################################"
        print "{:^159}".format("FLOATING POINT ARF")
        print "###############################################################################################################################################################"    
        reg_names = ["F0", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13", "F14", "F15"]
        print row_format.format(*reg_names)
        print row_format.format(*self.fp_registers[0:16])
        reg_names = ["F16", "F17", "F18", "F19", "F20", "F21", "F22", "F23", "F24", "F25", "F26", "F27", "F28", "F29", "F30", "F31"]
        print row_format.format(*reg_names)
        print row_format.format(*self.fp_registers[16:32])
        print