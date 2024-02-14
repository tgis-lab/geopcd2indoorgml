'''
Created on 2023年6月24日

@author: Zhiyong Wang
'''

import numpy as np

class UTMBbox:
    
    def __init__(self, **kwargs):
        if len(kwargs) == 8:
            self.utm0 =  kwargs["utm0"];
            self.utm1 = kwargs["utm1"] 
            self.utm2 =  kwargs["utm2"]
            self.utm3 = kwargs["utm3"]; 
            self.utm4 = kwargs["utm4"]; 
            self.utm5 = kwargs["utm5"];
            self.utm6 = kwargs["utm6"]; 
            self.utm7 = kwargs["utm7"];
        else:
            raise ValueError("Bbox argumments not correct!")  
    
    def getArray(self):
        
        utm_bbox_array = np.array([
                self.utm0,
                self.utm1,
                self.utm2,
                self.utm3,
                self.utm4,
                self.utm5,
                self.utm6,
                self.utm7,
            ],
            dtype=np.float64,
            )
        return utm_bbox_array
    
    
    def __str__(self):
        return ("utm0={0}; utm1={1}; utm2={2}; utm3= {3}; utm4={4}; utm5={5}; utm6={6}; utm7={7}").format(
            self.utm0, self.utm1, self.utm2, self.utm3, self.utm4, self.utm5, self.utm6, self.utm7);        