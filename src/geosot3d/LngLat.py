'''
Created on 2023年6月24日

@author: Zhiyong Wang
'''

# for TypeError: 'module' object is not callable
# https://www.cnblogs.com/herbert/p/13458276.html
from src.geosot3d.LngLatSegments import LngLatSegments

class LngLat:
    
    def __init__(self, *args):
        
        if len(args)== 1:
            dms = args[0]
            self.__init__fromDMS(dms)
        elif len(args)== 2:
            if isinstance(args[0], float):
                lng = args[0]
                lat = args[1]
                self.__init__fromLngLat(lng, lat)
            else:
                lCode = args[0]
                bCode = args[1]
                self.__init__fromLBcode(lCode, bCode)
        else:
            raise ValueError("arguments not correct!")

    def __str__(self):
        str = ''
        str += f'lat : {self.lat.getDMS()}; lon : {self.lng.getDMS()}\n'
        return str
    
    
    def __init__fromLngLat(self, lng, lat):       
        self.lng = LngLatSegments(lng);
        self.lat = LngLatSegments(lat);


    def __init__fromDMS(self, dms):
        str = dms.split(",");
        self.lat = LngLatSegments(str[0]);
        self.lng =  LngLatSegments(str[1]);


    def __init__fromLBcode(self, lCode, bCode):
        self.lng = LngLatSegments(lCode, True);
        self.lat = LngLatSegments(bCode, False); #lCode, bCode 32 bits
  

    def getLat(self):
        return self.lat;
    
    
    def getLng(self):
        return self.lng;

