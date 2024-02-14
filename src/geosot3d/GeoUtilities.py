'''
Created on 2023年6月26日

@author: Zhiyong Wang
refer to: https://en.proft.me/2015/09/20/converting-latitude-and-longitude-decimal-values-p/
'''

import re
import pyproj
from shapely import Point
from shapely.ops import transform




class GeoUtilities:
    
    i= 0
    
    @classmethod
    def wgs_to_utm(cls, a):
        lng = a[0]
        lat = a[1]
        hei = a[2]
        
        #wgs84_pt = Point(-72.2495, 43.886)
        #wgs84_pt = Point(113.28005773, 23.07074316, 10)
        wgs84_pt = Point(lng, lat)
        #print("wgs84_pt", wgs84_pt)
        wgs84 = pyproj.CRS('EPSG:4326')
        #utm = pyproj.CRS('EPSG:4479') # china
        #utm = pyproj.CRS('EPSG:32755') #  Australia
        utm = pyproj.CRS('EPSG:2062') #  spain
        project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform
        utm_point = transform(project, wgs84_pt)
        #print("utm_point", utm_point)
        if(cls.i%1000==0):
            print ("has translated ", cls.i)
        cls.i = cls.i + 1    
            
        #return [utm_point.x+2320936, utm_point.y-5392937, hei*1000]
        return [utm_point.x, utm_point.y, hei*1000] 
    def dms2dd(self, degrees, minutes, seconds, direction):
        dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
        if direction == 'S' or direction == 'W':
            dd *= -1
        return dd;

    def dd2dms(self, deg):
        d = int(deg)
        md = abs(deg - d) * 60
        m = int(md)
        sd = (md - m) * 60
        return [d, m, sd]

    def parse_dms(self, dms):
        
        list = re.split(r'°|\'|\"', dms) 
        D = int(list[0].strip());
        M = int(list[1].strip());
        seconds = float(list[2].strip());
        S = int(seconds);
        dotSeconds = (seconds - S) * 2048;
        S11 = round(dotSeconds);
        half = list[3].strip();
        if (half == "S" or half == "W"):
            G = 1; 
        elif (half == "N" or half == "E"): 
            G = 0;
        else:
            raise ValueError("save must be True if recurse is True")
            
        isLng = half == "W" or half == "E";
        
        return [G, D, M, S, S11, isLng]


    def parseDegree(self, degree, degreePresion, secondPresion):
        G = 1 if degree <0 else 0
        rd = abs(round(degree, degreePresion));
        D = int(rd); # converted signed to unsigned
        minutes = (rd - D) * 60;
        M = int(minutes)  # converted signed to unsigned
        seconds = round((minutes - M) * 60, secondPresion);
        S = int(seconds) # converted signed to unsigned
        dotSeconds = (seconds - S) * 2048;
        S11 = round(dotSeconds); # converted signed to unsigned
        return [G, D, M, S, S11]



    @staticmethod
    def decimalDgreeToDMS(dd, precision = 5):
        degrees = int(dd);
        minutes = (dd - degrees) * 60;
        seconds = ((minutes - int(minutes)) * 60);
        return ("{0}° {1}' {2}\"").format(
                abs(degrees), abs(int(minutes)),
                round(abs(seconds), precision));

    
    @staticmethod
    def getGeosotSteps(level):
        
        if level == 27: # 1/64 sec
            return [1/64, 1/64, 0.5]
        
        elif level == 28: # 1/128 sec
            return [1/128, 1/128, 0.25]
        
        elif level == 29: # 1/256 sec
            return [1/256, 1/256, 0.125]
        else:
            print("level= ", level, " is not correct!")
            return []
    
    
    @staticmethod
    def getManhattanDist(tile1, tile2, level):
        
        dist_dic = {}            
        lat_diff = tile1.getCornerLat()- tile2.getCornerLat()# in degree
        lng_diff = tile1.getCornerLng()- tile2.getCornerLng()  # in degree
        hei_diff = tile1.getCornerHeight()- tile2.getCornerHeight() # in km 
        steps = GeoUtilities.getGeosotSteps(level) # in sec, in sec, in meter
        
        lat_dist = round(abs(lat_diff*3600)/steps[0])
        lng_dist = round(abs(lng_diff*3600)/steps[1])
        hei_dist = round(abs(hei_diff*1000)/steps[2])
        
        dist_dic["lat_dist"] = lat_dist
        dist_dic["lng_dist"] = lng_dist
        dist_dic["hei_dist"] = hei_dist
        dist_dic["total_dist"] = lat_dist + lng_dist + hei_dist
        
        return dist_dic