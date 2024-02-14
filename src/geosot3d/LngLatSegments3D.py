'''
Created on 2023年6月24日

@author: Zhiyong Wang
'''
from src.geosot3d.GeoUtilities import GeoUtilities
from src.geosot3d.LngLatSegments import LngLatSegments
from src.geosot3d.Height import Height

class LngLatSegments3D(LngLatSegments):
    
    DegreePresion = 6
    SecondPresion = 4  # 1/2048=0.48828125e-3
                            # 4 bits for relative precision
                            # 11 bits for absolute precision


    IsLng = False
   
    G = 1 #  1 = negative，0 = positive
    
    LngDic = {"N": True,"E": True,"W": False,"S": False}
    GDic   = {"N": 0,"E": 0,"W": 1,"S": 1} 
    
    
    # only for height 
    def __init__(self, *args):
        
        
        if len(args)== 2:
            level = args[1]
            H = Height(level)
            if isinstance(args[0], float):
                self.height = args[0]
                heightDegree = H.calc_geosot_n(self.height, Height.theta0)
                LngLatSegments.__init__(self, heightDegree)
                self.heightCode = LngLatSegments.getCode(self)
            else:
                self.heightCode = args[0]
                LngLatSegments.__init__(self, args[0], False)
                self.height = H.calc_geosot_Hn(self.degree)

        else:
            raise ValueError("arguments not correct!")
    
    # in meters    
    def getHeight(self):
        return self.height;

    # convert height to 32bit 
    def getCode(self):      
        return self.heightCode


       





