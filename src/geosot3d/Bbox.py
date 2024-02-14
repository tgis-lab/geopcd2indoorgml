'''
Created on 2023年6月24日

@author: Zhiyong Wang
'''


class Bbox:
    
    def __init__(self, **kwargs):
        
        
        if len(kwargs) == 4:
            self.west =  kwargs["west"];
            self.south = kwargs["south"] 
            self.east =  kwargs["east"]
            self.north = kwargs["north"]; 

        elif len(kwargs) == 6:
            self.west =  kwargs["west"];
            self.south = kwargs["south"] 
            self.east =  kwargs["east"]
            self.north = kwargs["north"]; 
            self.low = kwargs["low"]; 
            self.high = kwargs["high"];
        else:
            raise ValueError("Bbox argumments not correct!")  
    
    def __str__(self):
        if not hasattr(self, "high"):
            return ("west={0}; south={1}; east={2}; north={3}").format(
                self.west, self.south, self.east, self.north);
        else: 
            return ("west={0}; south={1}; east={2}; north= {3}; low={4}; high={5}").format(
                self.west, self.south, self.east, self.north, self.low, self.high);        
         