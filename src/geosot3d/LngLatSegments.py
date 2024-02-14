'''
Created on 2023年6月24日

@author: Zhiyong Wang
'''
from src.geosot3d.GeoUtilities import GeoUtilities

class LngLatSegments(object):
    
    DegreePresion = 10
    SecondPresion = 4  # 1/2048=0.48828125e-3
                            # 4 bits for relative precision
                            # 11 bits for absolute precision


    IsLng = False
    G = 1 #  1 = negative，0 = positive
    
    LngDic = {"N": True,"E": True,"W": False,"S": False}
    GDic   = {"N": 0,"E": 0,"W": 1,"S": 1} 
    
  
    def __init__(self, *args):
        
        if len(args)==1:
            if isinstance(args[0], float):
                degree = args[0]
                self.__init__fromDegree(degree)
                
            else: 
                dms = args[0]
                self.__init__fromDMS(dms)
        elif len(args) == 2:
            x = args[0]
            isL = args[1]
            self.__init__fromCode(x, isL)
            
        else:
            raise ValueError("arguments not correct!")
                
    def __init__fromCode(self, x, isL):
        self.G = x >> 31;           # 1b
        self.D = (x >> 23) & 0xFF;  # 8b
        self.M = (x >> 17) & 0x3F;  # 6b
        self.S = (x >> 11) & 0x3F;  # 6b
        self.S11 = x & 0x7FF;       # 11b
        self.IsLng = isL 
        self.setCode()
        self.convertCodeToDegree()

    def __init__fromDegree(self, degree):
        uti = GeoUtilities();
        var = uti.parseDegree(degree,  LngLatSegments.DegreePresion, LngLatSegments.SecondPresion)
        self.G = var[0]
        self.D = var[1]
        self.M = var[2]
        self.S = var[3]
        self.S11= var[4]
        self.degree = degree
        self.setCode()

        
    def __init__fromDMS(self, dms):

        uti = GeoUtilities();
        var = uti.parse_dms(dms)
        self.G = var[0]
        self.D = var[1]
        self.M = var[2] 
        self.S = var[3]
        self.S11 = var[4] 
        self.isLng = var[5]
        self.setCode()
        self.convertCodeToDegree()

  
    def convertCodeToDegree(self):
        degree = self.D + self.M / 60.0 + self.S / 3600.0 + self.S11/2048/3600;
        if (self.G > 0):
            degree = -degree;
        
        self.degree = degree
        return;

    def getDegree(self):
        return self.degree

    def getDMS(self):
        return ("{0}° {1}' {2}\" {3} {4}").format(
                self.D, self.M, self.S, self.S11, self.getHalfCharactor());

    
    def setCode(self):
        
        #return self.G << 31 | self.D << 23 | self.M << 17 | self.S << 11 | self.S11;
        h1 = self.G << 31
        h2  = self.D << 23
        h3 = self.M << 17
        self.code =  h1 | h2 | h3 | self.S << 11 | self.S11;
        return;
    
    
    def getCode(self):

        return self.code
    
        
    def getHalfCharactor(self):
        if (self.IsLng):
            if (self.G == 1):
                return "W";
            else:
                return "E";
            
        else:
            if (self.G == 1):
                return "S";
            else: 
                return "N";


       





