'''
Created on 2023年6月24日

@author: Zhiyong Wang
'''

class CellSize:
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
    
    def getCellSizeInDegree(self, i):
        
        if (i >= 0 and i <= 9):
            return pow(2, 9 - i);
            
        if (i >= 10 and i <= 15):
            return pow(2, 15 - i) / 60;
        
        if (i >= 16 and i <= 32):
                return pow(2, 21 - i) / 3600;

        if (i < 0 or i > 32):
            print("i is not right, i = ", i)
            return -1;

      