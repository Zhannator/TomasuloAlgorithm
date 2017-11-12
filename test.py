#!/usr/bin/python
# -*- coding: utf-8 -*-

from sys import argv
import numpy as np

timing_table = [] # needs to be updated during execution time (pc, instruction, column for each stage)

def time_table_print():
    global timing_table
    print "###############################################################################################################################################################"
    print "{:^159}".format("TIMING TABLE")
    print "###############################################################################################################################################################"    
    column_names = [ "PC", "INSTRUCTION", "ISSUE", "EX_S", "EX_F", "MEM_S", "MEM_F", "WB", "COMMIT_S", "COMMIT_F"]
    row_format ="{:^16}" * len(column_names)
    print row_format.format(*column_names)
    for tt_entry in timing_table:
        tt_entry_list = np.array([tt_entry["PC"], tt_entry["instruction"], tt_entry["issue"], tt_entry["ex_start"], tt_entry["ex_finish"], tt_entry["mem_start"], tt_entry["mem_finish"], tt_entry["wb"], tt_entry["commit_start"], tt_entry["commit_finish"]])
        print row_format.format(*tt_entry_list)

def timing_table_add(PC, instruction, clock_cycle):
    global timing_table
    timing_table_entry = {
        "PC" : PC,
        "instruction" : instruction,
        "issue" : clock_cycle,
        "ex_start" : "-",
        "ex_finish" : "-",
        "mem_start" : "-",
        "mem_finish" : "-",
        "wb" : "-",
        "commit_start" : "-",
        "commit_finish" : "-"
    }
    timing_table.append(timing_table_entry.copy()) 
    
def arf_print(int_registers, fp_registers):
    print "###############################################################################################################################################################"
    print "{:^159}".format("ARF")
    print "###############################################################################################################################################################"    
    row_format ="{:^10}" * 8
    reg_names = ["R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7"]
    print row_format.format(*reg_names)
    print row_format.format(*int_registers[0:8])
    reg_names = ["R8", "R9", "R10", "R11", "R12", "R13", "R14", "R15"]
    print row_format.format(*reg_names)
    print row_format.format(*int_registers[8:16])
    reg_names = ["R16", "R17", "R18", "R19", "R20", "R21", "R22", "R23"]
    print row_format.format(*reg_names)
    print row_format.format(*int_registers[16:24])
    reg_names = ["R24", "R25", "R26", "R27", "R28", "R29", "R30", "R31"]
    print row_format.format(*reg_names)
    print row_format.format(*int_registers[24:32])
    print
    print "###############################################################################################################################################################"
    print "{:^159}".format("FLOATING POINT ARF")
    print "###############################################################################################################################################################"    
    reg_names = ["F0", "F1", "F2", "F3", "F4", "F5", "F6", "F7"]
    print row_format.format(*reg_names)
    print row_format.format(*fp_registers[0:8])
    reg_names = ["F8", "F9", "F10", "F11", "F12", "F13", "F14", "F15"]
    print row_format.format(*reg_names)
    print row_format.format(*fp_registers[8:16])
    reg_names = ["F16", "F17", "F18", "F19", "F20", "F21", "F22", "F23"]
    print row_format.format(*reg_names)
    print row_format.format(*fp_registers[16:24])
    reg_names = ["F24", "F25", "F26", "F27", "F28", "F29", "F30", "F31"]
    print row_format.format(*reg_names)
    print row_format.format(*fp_registers[24:32])

def mem_print(memory):
    print "###############################################################################################################################################################"
    print "{:^159}".format("MEMORY")
    print "###############################################################################################################################################################"  
    row_format ="{:^10}" * 16
    print row_format.format(*memory[0:16])
    print row_format.format(*memory[16:32])
    print row_format.format(*memory[32:48])
    print row_format.format(*memory[48:64])

# TT TEST
timing_table_add(0, "Add.d R1, R2, R3", 1)    
timing_table_add(4, "Ld F4, 8(R1)", 2)    
timing_table_add(8, "Bne R2, R3, -3", 3)
time_table_print()
print

# REG TEST
int_registers = [] # 32 registers by DLX standard
fp_registers = [] # 32 registers by DLX standard
int_registers = [0]*32
fp_registers = [0]*32
int_registers[1]=10
int_registers[2]=20
fp_registers[2]=30.1
arf_print(int_registers, fp_registers)
print

# MEM TEST
memory = [0]*64 # 265B (64W)
memory[4]=1
memory[8]=2
memory[12]=3.4
mem_print(memory)
print