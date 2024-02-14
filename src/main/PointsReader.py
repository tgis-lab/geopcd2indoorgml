'''
Created on 2023年8月8日

@author: Administrator
'''
import laspy
import numpy as np
from src.geosot3d.GeoUtilities import GeoUtilities as gu
from src.geosot3d.Tile3D import Tile3D
from xyconvert import wgs2gcj



class PointsReader(object):
    
    green = [1,0,0,0.5]
    red = [0,1,0,0.5]
        
    def __init__(self, _level):

        self.id_to_tile = {} 
        self.point_to_tile = {}
        self.level = _level

        return
    
    def converToDMS(self, lng, lat) -> str:
        lng_dms = gu.decimalDgreeToDMS(lng)+" E"
        lat_dms = gu.decimalDgreeToDMS(lat)+" S"
        dms = lat_dms +", " +lng_dms
        return dms
    
    
    def buildWholeSpace(self, level):
        points = self.wholespace_gcj_pts
        [rows, cols] = points.shape
        for i in range(rows):
            if (i%10000==0):
                print("has processed whole points", i)
                #if (i>200000):
                #    print("The total num of Tiles = ", len(id_to_tile), "Non Navi Tiles = ", len(self.non_navi_tiles), "Navi Tiles = ", len(self.navi_tiles))
                #    return id_to_tile
                
            _lng = points[i, 0]
            _lat = points[i, 1]
            _hei = points[i, 2]/1000
            _dms = self.converToDMS(_lng, _lat)
            _3dtile = Tile3D(_dms, _hei, level)
            if _3dtile.__str__() in self.id_to_tile:
            #print("already in ", _3dtile.__str__())
                continue
            self.id_to_tile[_3dtile.__str__()]=_3dtile
        print("The total num of Tiles in the whole space = ", len(self.id_to_tile))
        return self.id_to_tile
        
    
    
    def convertPtsToTiles(self, points:np.ndarray, level:int) ->  dict:
        
        [rows, cols] = points.shape
        for i in range(rows):
            if (i%10000==0):
                print("has processed points", i)
                #if (i>200000):
                #    print("The total num of Tiles = ", len(id_to_tile), "Non Navi Tiles = ", len(self.non_navi_tiles), "Navi Tiles = ", len(self.navi_tiles))
                #    return id_to_tile
                
            _lng = points[i, 0]
            _lat = points[i, 1]
            _hei = points[i, 2]/1000
            _label = points[i, 3]
            
            _dms = self.converToDMS(_lng, _lat)
            _3dtile_new = Tile3D(_dms, _hei, level)
            _3dtile_new.add_pt_label(_label)
            
            if _3dtile_new.__str__() in self.point_to_tile:
                _3dtile_old = self.point_to_tile[_3dtile_new.__str__()]
                _3dtile_old.add_pt_label(_label)
                continue
            self.point_to_tile[_3dtile_new.__str__()]=_3dtile_new
            #print("_3dtile bbox ", _3dtile_new, _3dtile_new.label, _3dtile_new.getBbox())
                      
        print("The total num of Point Tiles from Las file = ", len(self.point_to_tile))
        return self.point_to_tile
            
   
    def get_points_from_las(self, las_path):
        las = laspy.read(las_path)
        print("The total num of points = ", las.header.point_count)

        las_x=np.array(las.x)
        las_y=np.array(las.y)
        las_z=np.array(las.z)
        las_l = np.array(las.classification)
        
        return las_x, las_y, las_z, las_l
   

    def get_points_from_txt(self, txt_path):
        with open(txt_path, 'r') as f:
            lines = f.readlines()
        data  = np.loadtxt(lines, delimiter =',')
        print("the shape of points from txt = ", data.shape)
        las_x = data[:, 0]
        las_y = data[:, 1]
        las_z = data[:, 2]
        las_l = data[:, 3]
        
        return las_x, las_y, las_z, las_l

   
    def get_points(self, las_file, txt_file):
        
        if len(las_file)!=0:
            points_x, points_y, points_z, points_l = self.get_points_from_las(las_file)
        else:
            points_x, points_y, points_z, points_l = self.get_points_from_txt(txt_file)            
        
        points_x_min = min(points_x)
        points_x_max = max(points_x)
        points_y_min = min(points_y)
        points_y_max = max(points_y)
        points_z_min = min(points_z)
        points_z_max = max(points_z) 
        
        step_x = 1/256 / 3600 # level = 29
        step_y = 1/256 / 3600 # level = 29
        step_z = 0.12
        print("las_x_min, las_x_max", points_x_min, points_x_max)
        wholespace_x = np.arange(points_x_min, points_x_max, step_x, dtype=float)
        wholespace_y = np.arange(points_y_min, points_y_max, step_y, dtype=float)
        wholespace_z = np.arange(points_z_min, points_z_max, step_z, dtype=float)
        #print("whole_space_x = ", wholespace_x)
        #print("whole_space_y = ", wholespace_y)
        #print("whole_space_z = ", wholespace_z)
        wholespace_mesh = np.meshgrid(wholespace_x, wholespace_y, wholespace_z)
        wholespace_points = np.vstack(wholespace_mesh).reshape(3,-1).T
        print("wholespace_points shape", wholespace_points.shape)
        whole_gcj_array = wgs2gcj(np.stack([wholespace_points[:,0], wholespace_points[:,1]], axis=1))
        wholespace_x_gcj = whole_gcj_array[:,0]
        wholespace_y_gcj = whole_gcj_array[:,1]
        #print("wholespace_points x ", wholespace_x_gcj.shape, min(wholespace_x_gcj), max(wholespace_x_gcj))
        self.wholespace_gcj_pts = np.stack([wholespace_x_gcj, wholespace_y_gcj, wholespace_points[:,2]],axis=1)
        
        
        #las_r=np.array(las.red) 
        #las_g=np.array(las.green)
        #las_b=np.array(las.blue)
        
        print(np.stack([points_x, points_y, points_z], axis=1))
        #np.savetxt('test.out', np.stack([points_x, points_y, points_z], axis=1))
        las_gcj_array = wgs2gcj(np.stack([points_x, points_y], axis=1))
        points_x_gcj = las_gcj_array[:,0]
        points_y_gcj = las_gcj_array[:,1]
        #print("las_gcj_array" , las_gcj_array)
        #print("wgs842gcj = ", las_x[0], las_y[0], las_x_gcj[0], las_y_gcj[0])
        
        self.las_gcj_pts = np.stack([points_x_gcj, points_y_gcj, points_z, points_l],axis=1)
        #colors=np.stack([las_r,las_g,las_b],axis=1)
        



if __name__ == "__main__":
    
    lasreader= PointsReader(27)
    #lasreader.process_las('../data/exit-a-points_23_18_23.las')
    las_file_path= "../data/result-gps2.las"
    txt_file_path = "../data/result-gps2.txt"
    lasreader.get_points("", txt_file_path)
    #lasreader.buildWholeSpace(27, True)
    lasreader.convertPtsToTiles(lasreader.las_gcj_pts, 27)
    
    

