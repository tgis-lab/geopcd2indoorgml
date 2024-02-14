'''
Created on 2023年8月30日

@author: Administrator
'''
import numpy as np
from src.geosot3d.GeoUtilities import GeoUtilities

class GlTFPointsProducer():
    
    def __init__(self):
        self.tile_count = 0
        self.tile_points = np.array([])
        self.tile_triangles =  np.array([])
        self.triangles_unit = np.array(
            [
                [0, 1, 2],
                [3, 2, 1],
                [1, 0, 4],
                [5, 4, 0],
                [3, 1, 6],
                [4, 6, 1],
                [2, 3, 7],
                [6, 7, 3],
                [0, 2, 5],
                [7, 5, 2],
                [5, 7, 4],
                [6, 4, 7], 
            ],
            dtype="uint32",
            )
        self.tile_colors = np.zeros([8, 3], dtype=np.float32)
        
        self.line_points = np.array([])
        self.line_triangles= np.array([])
        self.line_colors= np.array([])
        
        alpha1 = 1.0
        alpha01 = 0.1
        alpha02 = 0.2
        alpha05 = 0.5
        alpha08 = 0.8
      
        self.np_red    = np.array([1,0,0,alpha1],dtype="float32",)  # red
        self.np_green  = np.array([0,1,0,alpha1],dtype="float32",)  # green
        self.np_blue   = np.array([0,0,1,alpha1],dtype="float32",)  # blue
        self.np_cyan = np.array([0,1,1,alpha1],dtype="float32",)  # cyan    
        self.np_purple = np.array([1,0,1,alpha1],dtype="float32",)  # purple
        self.np_yellow = np.array([1,1,0,alpha1],dtype="float32",)  # yellow
        self.np_white = np.array([1,1,1,alpha01],dtype="float32",)  # white 
        self.np_unknown1 = np.array([0.5,0.5,0.5,alpha1],dtype="float32",)        
        self.np_dark = np.array([0.2,0.2,0.2,alpha1],dtype="float32",) # dark 

        
        self.label_roof = 8
        self.label_rail = 1
        self.label_wall = 6
        self.label_ground = 5
        
        self.label_navi_ground = 25
        self.label_navi_wall = 26
        
        self.label_nonnavi_roof = 18
        self.label_nonnavi_rail = 11
        
        
        
        return
    
    
    
    def transformTilesToPoints(self, tiles):
               
        for id, tile in tiles.items():
            bbox = tile.getBbox()
            label = tile.label
            if label == 1:
                color_arr = self.np_red  # red
            elif label == 6:
                color_arr = self.np_yellow      
            elif label < 10:
                color_arr = self.np_cyan             
            elif label < 20:
                color_arr = self.np_green
            elif label == 25:
                color_arr = self.np_blue
            elif label == 26:
                color_arr = self.np_purple
            else: 
                color_arr = self.np_white        
                
            tile_points_bbox = np.array([
                [bbox.west, bbox.south, bbox.high*1000],
                [bbox.east, bbox.south, bbox.high*1000],
                [bbox.west, bbox.north, bbox.high*1000],
                [bbox.east, bbox.north, bbox.high*1000],
                [bbox.east, bbox.south, bbox.low*1000],
                [bbox.west, bbox.south, bbox.low*1000],
                [bbox.east, bbox.north, bbox.low*1000],
                [bbox.west, bbox.north, bbox.low*1000],
            ],
            dtype=np.float64,
            )
            # converting from wgs84 to UTM
            #tile_points = np.apply_along_axis(GeoUtilities.wgs_to_utm, 1, tile_points_bbox)
            #tile_points = np.float32(tile_points)
            tile_points = np.float32(tile_points_bbox)
            print("tile_points_bbox = ", tile_points_bbox, " ,tile_points = ", tile_points)
            tile_points = np.round(tile_points, 3)
            if self.tile_count == 0:
                self.tile_points = tile_points
                self.tile_triangles = self.triangles_unit
                self.tile_colors = np.ones((len(tile_points),1), dtype="float32")*color_arr
            else:
                self.tile_points = np.append(self.tile_points, tile_points, axis = 0)
                self.tile_triangles = np.append(self.tile_triangles, self.triangles_unit+8*(self.tile_count), axis = 0)
                self.tile_colors = np.append(self.tile_colors, np.ones((len(tile_points),1), dtype="float32")*color_arr, axis = 0)
           
            #print("self.tile_points", self.tile_points.shape, self.tile_points)
            #print("self.tile_triangles", self.tile_triangles.shape, self.tile_triangles)
            #print("self.tile_colors", self.tile_colors.shape, self.tile_colors.dtype, self.tile_colors)
            self.tile_count =  self.tile_count + 1 
    
    
    
    def transformUTMToPoints(self, tiles, offset):
               
        num = 0        
     
        
        for id, tile in tiles.items():
            
            num = num + 1
            if(num%10000==0):
                print("utm tiles to gltf = ", num)
            
            utm_bbox = tile.getUTMBbox()
            label = tile.label
            if label == 1: # railway
                color_arr = self.np_red  # red
            elif label == 3: # stair
                color_arr = self.np_unknown1
            elif label == 4: # ramp
                color_arr = self.np_dark    
            elif label == 5: # ground
                color_arr = self.np_green
            elif label == 6 : # wall 
                color_arr = self.np_cyan      
            elif label == 8 : # roof 
                color_arr = self.np_yellow             
            elif label < 10: # others  == 0
                print("label = ", label, tile.__str__()) 
                color_arr = self.np_white             
            elif label < 20: # non-navi
                color_arr = self.np_purple
            elif label == 25:
                color_arr = self.np_blue #self.np_blue
            elif label == 26:
                #print("label = ", label, tile.__str__())
                color_arr = self.np_blue
            else:
                print("label = ", label, tile.__str__())
                color_arr = self.np_unknown1   
            
            tile_utm_points = utm_bbox.getArray()
            
            offset_array = np.array([
                offset,
                offset,
                offset,
                offset,
                offset,
                offset,
                offset,
                offset,
            ],
            dtype=np.float64,
            )
            
            tile_utm_points = tile_utm_points - offset_array
            
            tile_utm_points = np.float32(tile_utm_points)
            #print("utm_bbox = ", utm_bbox, " ,tile_utm_points = ", tile_utm_points)
            tile_utm_points = np.round(tile_utm_points, 6)
            if self.tile_count == 0:
                self.tile_points = tile_utm_points
                self.tile_triangles = self.triangles_unit
                self.tile_colors = np.ones((len(tile_utm_points),1), dtype="float32")*color_arr
            else:
                self.tile_points = np.append(self.tile_points, tile_utm_points, axis = 0)
                self.tile_triangles = np.append(self.tile_triangles, self.triangles_unit+8*(self.tile_count), axis = 0)
                self.tile_colors = np.append(self.tile_colors, np.ones((len(tile_utm_points),1), dtype="float32")*color_arr, axis = 0)
           
            #print("self.tile_points", self.tile_points.shape, self.tile_points)
            #print("self.tile_triangles", self.tile_triangles.shape, self.tile_triangles)
            #print("self.tile_colors", self.tile_colors.shape, self.tile_colors.dtype, self.tile_colors)
            self.tile_count =  self.tile_count + 1 