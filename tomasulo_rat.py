
#!/usr/bin/python
# -*- coding: utf-8 -*-

# Tomasulo RAT

int_rat = [] # needs to be initialized, same size as ARF
fp_rat = [] # needs to be initialized, same size as ARF

       
def main():
    rat_initialize()
    
    print int_rat
    print fp_rat
    
    
def rat_initialize():
    # initialize rat
    
    global int_rat
    global fp_rat
    for i in range(0, 32):
        int_rat.append("R" + str(i))
        fp_rat.append("F" + str(i))
    
    
def fp_rat_update(fp_reg, fp_value):
    #update mapping for Floating Point RAT
    
    fp_rat_update_index = int(fp_reg.split("R")[1])
    fp_rat[fp_rat_update_index] = fp_value
    
    
def int_rat_update(int_reg, int_value):
    #update mapping for Integer RAT
    
    int_rat_update_index = int(int_reg.split("R")[1])
    int_rat[int_rat_update_index] = int_value
    
    
  
if __name__ == "__main__":
    main()