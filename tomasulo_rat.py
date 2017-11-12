#!/usr/bin/python
# -*- coding: utf-8 -*-

# Tomasulo RAT

class RATobject:
    int_rat = [] # same size as ARF
    fp_rat = [] # same size as ARF
    
    def rat_initialize(self):
        # initialize rat
        for i in range(0, 32):
            self.int_rat.append("R" + str(i))
            self.fp_rat.append("F" + str(i)) 
        
    def int_rat_get(self, int_reg):
        # get current value in int_reg location
        int_rat_update_index = int(int_reg.split("R")[1])
        return self.int_rat[int_rat_update_index]
    
    def fp_rat_get(self, fp_reg):
        # get current value in int_reg location
        fp_rat_update_index = int(fp_reg.split("F")[1])
        return self.fp_rat[fp_rat_update_index]
    
    def int_rat_update(self, int_reg, int_value):
        #update mapping for Integer RAT
        int_rat_update_index = int(int_reg.split("R")[1])
        self.int_rat[int_rat_update_index] = int_value  

    def fp_rat_update(self, fp_reg, fp_value):
        #update mapping for Floating Point RAT
        fp_rat_update_index = int(fp_reg.split("F")[1])
        self.fp_rat[fp_rat_update_index] = fp_value