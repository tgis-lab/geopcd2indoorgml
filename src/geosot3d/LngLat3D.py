'''
Created on 2023年6月24日

@author: Zhiyong Wang
'''


from src.geosot3d.LngLatSegments3D import LngLatSegments3D
from src.geosot3d.LngLat import LngLat

class LngLat3D(LngLat):
    
    def __init__(self, *args):
        
        if len(args)== 3:
            dms = args[0]
            h = args[1]
            l = args[2]
            LngLat.__init__(self, dms)
            self.hei = LngLatSegments3D(h, l)
        elif len(args)== 4:
            if isinstance(args[0], float):
                lng = args[0]
                lat = args[1]
                h = args[2] 
                l = args[3] 
                LngLat.__init__(self, lng, lat)
                self.hei = LngLatSegments3D(h, l)
            else:
                lCode = args[0]
                bCode = args[1]
                hCode = args[2]
                l = args[3]
                LngLat.__init__(self, lCode, bCode)
                self.hei = LngLatSegments3D(hCode, l)
        else:
            raise ValueError("arguments not correct!")

    def __str__(self):
        str = ''
        str += f'lat : {self.lat.getDMS()}; lon : {self.lng.getDMS()} ; hei : {self.hei.getHeight()}\n'
        return str
    
   
    def getHei(self):
        return self.hei


