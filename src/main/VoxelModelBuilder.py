'''
Created on 2023年8月28日

@author: Administrator
'''
import time
import numpy as np
from src.visualization.GlTFPointsProducer import GlTFPointsProducer
from src.visualization.GLTFProducer import GLTFProducer
from src.main.PointsReader import PointsReader
from src.main.XmlWriter import XmlWriter
from src.routing.Router import Router
import src.postgis.init_database as db
import src.postgis.utility_fun as uf



class VoxelModelBuilder(object):
    
    def __init__(self, las_file_path, txt_file_path, _level, test_mode, points_to_tiles_mode, srid):
        
        self.level = _level
        if test_mode:
            print("using test_mode...")
        if points_to_tiles_mode:
            # extract tiles from points
            lasreader= PointsReader(_level)
            lasreader.get_points(las_file_path, txt_file_path)
            self.id_to_tile = lasreader.buildWholeSpace(self.level)
            self.point_to_tile = lasreader.convertPtsToTiles(lasreader.las_gcj_pts, self.level)
            self.id_to_tile.update(self.point_to_tile)
            self.dump_tiles_to_db(srid)
            self.id_to_tile = {}  # empty tiles
            self.point_to_tile = {}
    
        # extract tiles from db        
        self.id_to_tile = db.buildWholeSpaceFromDB(self.level)
        self.point_to_tile = db.buildPointTilesFromDB(self.level)
            
        self.navi_tiles = {}
        self.non_navi_tiles = {}                
        
        self.label_rail = 1
        self.label_green = 2
        self.label_stairs = 3
        self.label_ground = 5
        self.label_wall = 6
        self.label_roof = 8
        self.label_navi_ground = 25
        self.label_navi_wall = 26
        self.label_nonnavi_roof = 18
        self.label_nonnavi_rail = 11
        self.label_route = 100
            
        return



    def dump_tiles_to_db(self, srid):
        print("dumping tiles into the database...")
        db.init_db(level, srid)
        db.dump_to_db(level, self.id_to_tile)
        db.update_all_voxel_labels(self.point_to_tile, level)
        db.update_utm_columns(level,srid)
    
    def hasNaviLabel(self, pt_tile):
        
        if str(float(self.label_ground)) in pt_tile.label_dict and pt_tile.label_dict.get(str(float(self.label_ground))) > 30:
            return True
        elif str(float(self.label_green)) in pt_tile.label_dict and pt_tile.label_dict.get(str(float(self.label_green))) > 30:
            return True
        elif str(float(self.label_stairs)) in pt_tile.label_dict and pt_tile.label_dict.get(str(float(self.label_stairs))) > 30:
            return True
        else:
            return False
    
    
       
    def deriveNaviVoxels(self):
        for id, pt_tile in self.point_to_tile.items():
            ## derive navi voxels
            #if (pt_tile.label == self.label_ground or pt_tile.label == self.label_green or pt_tile.label == self.label_stairs) and pt_tile.getAboveTile().__str__() in self.id_to_tile: 
            if self.hasNaviLabel(pt_tile) and pt_tile.getAboveTile().__str__() in self.id_to_tile: 
                if self.id_to_tile[pt_tile.getAboveTile().__str__()].label == 0:
                    above_tile = pt_tile.getAboveTile()
                    self.id_to_tile[above_tile.__str__()].label = self.label_navi_ground
                    self.navi_tiles[above_tile.__str__()] = self.id_to_tile[above_tile.__str__()]  ## add the above tile                
            
            elif pt_tile.label == self.label_rail and  pt_tile.getAboveTile().__str__() in self.id_to_tile: ## derive non-navi voxels    
                if self.id_to_tile[pt_tile.getAboveTile().__str__()].label == 0:
                    self.id_to_tile[pt_tile.getAboveTile().__str__()].label = self.label_nonnavi_rail
                    self.non_navi_tiles[pt_tile.getAboveTile().__str__()] = self.id_to_tile[pt_tile.getAboveTile().__str__()]  ## add the above tile      
 
            ## consider spaces around wall as navigable spaces
            elif pt_tile.label == self.label_wall and pt_tile.getWestTile().__str__() in self.id_to_tile:
                if self.id_to_tile[pt_tile.getWestTile().__str__()].label == 0:
                    self.id_to_tile[pt_tile.getWestTile().__str__()].label = 26
            elif pt_tile.label == self.label_wall and pt_tile.getEastTile().__str__() in self.id_to_tile:
                if self.id_to_tile[pt_tile.getEastTile().__str__()].label == 0: 
                    self.id_to_tile[pt_tile.getEastTile().__str__()].label = 26
            elif pt_tile.label == self.label_wall and pt_tile.getNorthTile().__str__() in self.id_to_tile: 
                if self.id_to_tile[pt_tile.getNorthTile().__str__()].label == 0:
                    self.id_to_tile[pt_tile.getNorthTile().__str__()].label = 26
            elif pt_tile.label == self.label_wall and pt_tile.getSouthTile().__str__() in self.id_to_tile: 
                if self.id_to_tile[pt_tile.getSouthTile().__str__()].label== 0:    
                    self.id_to_tile[pt_tile.getSouthTile().__str__()].label = 26
            

        
 
 
    def regionGrowing3D(self):
   
        open_set = self.navi_tiles.copy()
        closed_set = {}
        while len(open_set) > 0:
            for _tile in list(open_set.values()):
                tile_neighbour_list = []
                neighbour_list_24 = _tile.get24ConnectedNeighbours()
                for x in neighbour_list_24:
                    if x.__str__() in self.id_to_tile:
                        tile_neighbour_list.append(x)
   
                for tile_neighbr in tile_neighbour_list:
                    if tile_neighbr.__str__() in closed_set:
                        continue
                    ## skip the neighbour that has above tie
                    if tile_neighbr.getAboveTile().__str__() in self.point_to_tile:
                        continue
                    if tile_neighbr.__str__() in self.id_to_tile:
                        neighbor_label =  self.id_to_tile[tile_neighbr.__str__()].label
                        if neighbor_label < 20 :
                            self.non_navi_tiles[tile_neighbr.__str__()]= self.id_to_tile[tile_neighbr.__str__()]
                        elif neighbor_label > 20:
                            if tile_neighbr.getBelowTile().__str__() in self.point_to_tile: # add neighbour if it has below point
                                _tile.connected_neighbours.append(tile_neighbr.__str__())
                                self.navi_tiles[tile_neighbr.__str__()]= self.id_to_tile[tile_neighbr.__str__()]
                                open_set[tile_neighbr.__str__()] = self.id_to_tile[tile_neighbr.__str__()]
                        else:  # ==0
                            continue

                        #print("_tile ", self.id_to_tile[_tile.__str__()].name, ", tile_neighbr.__str__ ", tile_neighbr.__str__(), " ; name = ", self.id_to_tile[tile_neighbr.__str__()].name, "self.id_to_tile[tile_neighbr.__str__()].label", self.id_to_tile[tile_neighbr.__str__()].label)
                #print("connected neigh size " , len(_tile.getConnectNeighbours()))
                closed_set[_tile.__str__()]=_tile # _tile into closed_set 
                open_set.pop(_tile.__str__())   
        return self.navi_tiles
        
        
                    
    # output_path = "../output/test_color2.glb"
    def exportToGltf(self, output_path, offset):
        line_points = np.array([
          [0, 0, 0],
          [0.000001, 0.000001, 0.000001],
          [0.000001, 0.000001, 0.000001],
          [0, 0, 0],
         ],dtype="float32",
        )
    
    
        line_positions = np.array([
          [0, 1],
          [2, 3]
         ], dtype="uint32",
        )
    
        line_colors = np.array([
          [1, 0, 0, 0.5],
          [1, 0, 0, 0.5],
          [1, 0, 0, 0.5],
          [1, 0, 0, 0.5]
         ], dtype="float32",
        ) 
            
        gp = GLTFProducer()    
        gl_points = GlTFPointsProducer()
        #gl_points.transformTilesToPoints(self.navi_tiles)   ### wgs84
        navi_plus_point_tiles =  self.navi_tiles.copy()
        navi_plus_point_tiles.update(self.point_to_tile)
        #self.id_to_tile.update(self.point_to_tile)
        gl_points.transformUTMToPoints(navi_plus_point_tiles, offset)      ### utm 
                
        print("rendering geosot", gl_points.tile_points, gl_points.tile_triangles, gl_points.tile_colors, output_path)
        gp.gltf_from_array(gl_points.tile_points, gl_points.tile_triangles, gl_points.tile_colors, line_points, line_positions, line_colors, output_path)
        (points_output, triangles_output, colors_output) = gp.decode_gltf()
        print("output array =", points_output, triangles_output, colors_output )
        print("output array size =", points_output.shape, triangles_output.shape, colors_output.shape)
        
if __name__ == "__main__":
    
    output_path = "../output/tspace_withcolor.glb"
    #las_file_path= "../data/exit-a-points_23_18_23.las"
    #las_file_path= "../data/Stationm2-gps-without-roof.las"
    #las_file_path= "../data/Sstationm2-gps.las"
    #las_file_path= "../data/2019-05-16_12-39-43_30pct_zebcamsh_norm - Cloud.las"
    #las_file_path= "../data/result-gps2-3.las"
    
    
    #txt_file_path = "../data/test_au_wgs84_data_gps.txt"
    #txt_file_path = "../data/Teleco-gps2.txt"
    txt_file_path = "../data/result-GPS2-4.txt"
    #txt_file_path = "../data/Minas_Labs-gps4.txt"
    output_xml_path = "../output/Indoorgml3.gml"
    test_mode = False
    points_to_tiles_mode = False
    set_zero_offset = False

    st = time.time()
    level = 28
    #srid = 4979  # world srid
    srid = 32755  # au srid
    #srid = 2062  # spain srid
    
    
    uf.target_table = 'voxels_au_32755'
    #uf.target_table = 'voxels_au_4979'
    #uf.target_table = 'voxels_teleco_2062'
    #uf.target_table = 'voxels_teleco_4979'
    #uf.target_table = 'voxels_minas_2062'
    #target_table = 'voxels_minas_4979'
    
    
    
    builder = VoxelModelBuilder("", txt_file_path, level, test_mode, points_to_tiles_mode, srid)
  
    
    print("finding navigable spaces...")
    print("Initializing, Non Navi Tiles = ", len(builder.non_navi_tiles), "Navi Tiles = ", len(builder.navi_tiles))  
    builder.deriveNaviVoxels()
    print("Before region growing, Non Navi Tiles = ", len(builder.non_navi_tiles), "Navi Tiles = ", len(builder.navi_tiles))  
    builder.regionGrowing3D()
    print("After region growing, Non Navi Tiles = ", len(builder.non_navi_tiles), "Navi Tiles = ", len(builder.navi_tiles))  
  
    print("calculating routes...")
    router = Router(builder.navi_tiles, level)
    index = 0

    # minas
    #ori = builder.navi_tiles["G200203020-103020-000130.1000732"]
    #des =  builder.navi_tiles["G200203020-103020-000130.1147127"]
    
    # teleco
    #ori = builder.navi_tiles["G200203020-102113-333013.1203375"] ## a bit problem
    #ori = builder.navi_tiles["G200203020-102113-333013.1213365"] 
    #des = builder.navi_tiles["G200203020-102113-333013.1107515"]
    
    # au 
    ori = builder.navi_tiles["G210210203-222013-220123.3713125"] 
    des = builder.navi_tiles["G210210203-222013-220132.2711065"]
    path_list = router.calculate(ori, des)
    print("the calculated path = ", path_list)
    for i in range(len(path_list)):
        path_node  = path_list[i]
        builder.navi_tiles[path_node].label = builder.label_route
        
  
  
  
    print("generating glb file...")
    if set_zero_offset:
        offset = [0,0,0]
    else:
        offset = db.getOffsetFromDB(level)
    builder.exportToGltf(output_path, offset)
   
    
    print("generating IndoorGML...")
    writer = XmlWriter(builder.navi_tiles)
    writer.generate_cells_from_tiles()
    writer.generate_states_transitions_from_tiles()
    writer.create_xml(output_xml_path)
  
    et = time.time()
    elapsed_time = et - st
    print('Execution time:', elapsed_time, 'seconds')        



    


    