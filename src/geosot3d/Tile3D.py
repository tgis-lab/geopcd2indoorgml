'''
Created on 2023年6月24日

@author: Zhiyong Wang
'''

from src.geosot3d.LngLatSegments import LngLatSegments
from src.geosot3d.CellSize import CellSize
from src.geosot3d.Bbox import Bbox
from src.geosot3d.Height import Height
from src.geosot3d.Morton3D import Morton3D
from src.geosot3d.UTMBbox import UTMBbox
from src.geosot3d.LngLat3D import LngLat3D
from src.geosot3d.LngLatSegments3D import LngLatSegments3D
from src.geosot3d.Tile import Tile

class Tile3D(Tile):
    '''
    classdocs
    '''
    def __init__(self, *args):
        
        self.label = 0
        self.label_dict = {}
        self.name = ""
        self.connected_neighbours=[]
        ## code, level      
        if len(args)== 1:
            code = args[0]
            self.__init__fromCode(code)
        ## dms, height, level     
        elif len(args)== 3:
            dms = args[0]
            h = args[1]
            l = args[2] 
            self.__init__fromDMS(dms, h, l)
        elif len(args)== 4:
            lCode = args[0]
            bCode = args[1]
            hCode = args[2] 
            level = args[3] 
            self.__init__fromLBHCode(lCode, bCode, hCode, level)
        else:
            raise ValueError("arguments not correct!")
        

        
    def __init__fromCode(self, code):
        level= 0
        id = 0
        
        for ele in code:
            if (ele.isdigit()):
                v = Tile3D.getDecodeChar(ele);
                shift = ((31 - level) * 3);
                id = id | v << shift;
                #print("id = ", bin(id)[2:].zfill(96))
                level = level + 1;
                
        self.code = id
        [lCode, bCode, hCode] = self.deCode(id)
        #print("lng decode = ", bin(id)[2:].zfill(96))
        #print("lng decode = ", bin(lCode)[2:].zfill(32))
        #print("lat decode = ", bin(bCode)[2:].zfill(32))
        #print("hei decode = ", bin(hCode)[2:].zfill(32))
        self.coord = LngLat3D(lCode, bCode, hCode, level);
        self.level = level
        self.corner = self.getCorner() 
    
    def __init__fromLBHCode(self, lCode, bCode, hCode, level):
        self.coord = LngLat3D(lCode, bCode, hCode, level);
        self.level = level
        self.setCode(); 
        self.corner = self.getCorner() 
    
    
            
    def __init__fromDMS(self, dms, h, l):
        self.dms = dms
        self.height = h    
        self.level = l
        self.coord = LngLat3D(dms ,self.height, l);
        self.setCode(); 
        self.corner = self.getCorner()       
        
    def setCode(self):
        m = Morton3D(dimensions=3, bits=32)
        L = self.coord.getLng().getCode();
        B = self.coord.getLat().getCode();
        H = self.coord.getHei().getCode();
        #print("lng bin = ", bin(L)[2:].zfill(32))
        #print("lat bin = ", bin(B)[2:].zfill(32))
        #print("hei bin = ", bin(H)[2:].zfill(32))
        self.code = m.pack(L, B, H);
        #print("code total = ", bin(self.code)[2:].zfill(96))
        return;

    ## lcode, Bcode, Hcode
    def deCode(self, code):
        m = Morton3D(dimensions=3, bits=32)
        var = m.unpack(code);
        return var;
    
        
    def getCoordLngCode(self):
        return self.coord.getLng().getCode();
    
    def getCoordLatCode(self):
        return self.coord.getLat().getCode() ;
    
    def getCoordHeiCode(self):
        return self.coord.getHei().getCode();
    
    
    def getCornerLng(self):
        L = LngLatSegments(self.corner.lng.getCode(), True);        
        return L.getDegree();
    
    def getCornerLat(self):
        B = LngLatSegments(self.corner.lat.getCode(), False);        
        return B.getDegree();
    
    def getCornerHeight(self):
        H = LngLatSegments3D(self.corner.hei.getCode(), self.level);
        return H.getHeight();
    
    
    
    @staticmethod
    def getDecodeChar(c):
        if (c == '1'):
            return 1
        if (c == '2'):
            return 2
        if (c == '3'):
            return 3
        if (c == '4'):
            return 4
        if (c == '5'):
            return 5 
        if (c == '6'):
            return 6 
        if (c == '7'):
            return 7 
        return 0
    
    # @staticmethod
    # def getDecodeChar(c):
    #     if (c == '1'):
    #         return (1).to_bytes(1, 'big');
    #     if (c == '2'):
    #         return (2).to_bytes(1, 'big');
    #     if (c == '3'):
    #         return (3).to_bytes(1, 'big'); 
    #     if (c == '4'):
    #         return (4).to_bytes(1, 'big'); 
    #     if (c == '5'):
    #         return (5).to_bytes(1, 'big'); 
    #     if (c == '6'):
    #         return (6).to_bytes(1, 'big'); 
    #     if (c == '7'):
    #         return (7).to_bytes(1, 'big');  
    #     return (0).to_bytes(1, 'big');

    def getBbox(self):
        cellSize = CellSize();
        cell = cellSize.getCellSizeInDegree(self.level);

        #print("xyz = ", self.corner.lng.getCode(), self.corner.lat.getCode(), self.corner.hei.getCode())
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) + 1) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level)) + 1) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level)) + 1) << (32 - self.level)
        #print("trtile_xyz = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        self.bbox = Bbox(west =  min(self.corner.getLng().getDegree(), trtile.corner.getLng().getDegree()),
                south = min(self.corner.getLat().getDegree(), trtile.corner.getLat().getDegree()),
                low =  min(self.corner.hei.getHeight(), trtile.corner.hei.getHeight()),
                
                east =  max(self.corner.getLng().getDegree(), trtile.corner.getLng().getDegree()),
                north = max(self.corner.getLat().getDegree(), trtile.corner.getLat().getDegree()),
                high = max(self.corner.hei.getHeight(), trtile.corner.hei.getHeight()))

        return self.bbox;
    
    
    def setUTMBbox(self, _utm0, _utm1, _utm2, _utm3, _utm4, _utm5, _utm6, _utm7):
        self.utmBox = UTMBbox(utm0=_utm0, utm1=_utm1, utm2=_utm2, utm3=_utm3, utm4=_utm4, utm5=_utm5, utm6=_utm6, utm7=_utm7)
    
    def getUTMBbox(self):
        return self.utmBox
        
    
    
    def getAboveTile(self):
        trtile_x = ((self.corner.lng.getCode() >> (32 - self.level)) ) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level)) ) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level)) + 1) << (32 - self.level)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
        

    
    def getBelowTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) ) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level)) ) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level)) - 1) << (32 - self.level)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
        

    ########west, east, north, south##############################################
    ########northwest, notrh east, southwest, southeast    #######################
    
        
    def getWestTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) -1) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level)) ) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))) << (32 - self.level)
        #print("trtile_xyz west = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    
    def getEastTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) +1) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level)) ) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))) << (32 - self.level)
        #print("trtile_xyz = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    

    
    def getNorthTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) ) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level))+1) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))) << (32 - self.level)
        #print("trtile_xyz = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    

    
    def getSouthTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) ) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level))-1) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))) << (32 - self.level)
        #print("trtile_xyz = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    
    
    
    def getNorthWestTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) -1) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level)) +1 ) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))) << (32 - self.level)
        #print("trtile_xyz west = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    
    def getNorthEastTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) +1) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level)) +1 ) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))) << (32 - self.level)
        #print("trtile_xyz = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    

    
    def getSouthWestTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) -1) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level))-1) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))) << (32 - self.level)
        #print("trtile_xyz = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    

    
    def getSouthEastTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) +1) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level))-1) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))) << (32 - self.level)
        #print("trtile_xyz = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    
    
    
    ########belowwest, beloweast, belownorth, belowsouth##############################################
    ########belownorthwest, belownotrheast, belowsouthwest, belowsoutheast    #######################
    
    def getBelowWestTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) -1) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level)) ) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))-1) << (32 - self.level)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    
    def getBelowEastTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) +1) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level)) ) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))-1) << (32 - self.level)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile

    def getBelowNorthTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) ) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level))+1) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))-1) << (32 - self.level)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    
    def getBelowSouthTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) ) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level))-1) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))-1) << (32 - self.level)
        #print("trtile_xyz = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    
    
    
    def getBelowNorthWestTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) -1) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level)) +1 ) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))-1) << (32 - self.level)
        #print("trtile_xyz west = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    
    def getBelowNorthEastTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) +1) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level)) +1 ) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))-1) << (32 - self.level)
        #print("trtile_xyz = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    

    
    def getBelowSouthWestTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) -1) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level))-1) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))-1) << (32 - self.level)
        #print("trtile_xyz = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    

    
    def getBelowSouthEastTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) +1) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level))-1) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))-1) << (32 - self.level)
        #print("trtile_xyz = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    
    
    
    ########abovewest, aboveeast, abovenorth, abovesouth##############################################
    ########abovenorthwest, abovenotrheast, abovesouthwest,abovesoutheast    #######################
    
    
    def getAboveWestTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) -1) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level)) ) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))+1) << (32 - self.level)
        #print("trtile_xyz = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    
    
    def getAboveEastTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) +1) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level)) ) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))+1) << (32 - self.level)
        #print("trtile_xyz = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    
    def getAboveNorthTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) ) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level))+1) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))+1) << (32 - self.level)
        #print("trtile_xyz = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    
    def getAboveSouthTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) ) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level))-1) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))+1) << (32 - self.level)
        #print("trtile_xyz = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile    
    
    
    def getAboveNorthWestTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) -1) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level)) +1 ) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))+1) << (32 - self.level)
        #print("trtile_xyz west = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    
    def getAboveNorthEastTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) +1) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level)) +1 ) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))+1) << (32 - self.level)
        #print("trtile_xyz = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    

    
    def getAboveSouthWestTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) -1) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level))-1) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))+1) << (32 - self.level)
        #print("trtile_xyz = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    

    
    def getAboveSouthEastTile(self):
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) +1) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level))-1) << (32 - self.level)
        trtile_z = ((self.corner.hei.getCode() >> (32 - self.level))+1) << (32 - self.level)
        #print("trtile_xyz = ", trtile_x, trtile_y, trtile_z)
        trtile = Tile3D(trtile_x, trtile_y, trtile_z, self.level);
        return trtile
    
    
    def get12ConnectedNeighbours(self):
        tile_neighbour_list = []
        
        tile_west = self.getWestTile()
        tile_east = self.getEastTile()
        tile_north = self.getNorthTile()
        tile_south = self.getSouthTile()
               
        tile_belowWest = self.getBelowWestTile()
        tile_belowEast = self.getBelowEastTile()
        tile_belowNorth = self.getBelowNorthTile()
        tile_belowSouth = self.getBelowSouthTile()
        
        tile_aboveWest = self.getAboveWestTile()
        tile_aboveEast = self.getAboveEastTile()
        tile_aboveNorth = self.getAboveNorthTile()
        tile_aboveSouth = self.getAboveSouthTile()
        
        tile_neighbour_list.append(tile_west)
        tile_neighbour_list.append(tile_east)
        tile_neighbour_list.append(tile_north)
        tile_neighbour_list.append(tile_south)
        
        tile_neighbour_list.append(tile_belowWest)
        tile_neighbour_list.append(tile_belowEast)
        tile_neighbour_list.append(tile_belowNorth)
        tile_neighbour_list.append(tile_belowSouth)

        tile_neighbour_list.append(tile_aboveWest)
        tile_neighbour_list.append(tile_aboveEast)
        tile_neighbour_list.append(tile_aboveNorth)
        tile_neighbour_list.append(tile_aboveSouth)
        
        return tile_neighbour_list
    
    
    
    def get24ConnectedNeighbours(self):
        tile_neighbour_list = []
        
        tile_west = self.getWestTile()
        tile_east = self.getEastTile()
        tile_north = self.getNorthTile()
        tile_south = self.getSouthTile()
         
        tile_northWest = self.getNorthWestTile()
        tile_northEast = self.getNorthEastTile()
        tile_southWest = self.getSouthWestTile()
        tile_southEast = self.getSouthEastTile()
        
        tile_belowWest = self.getBelowWestTile()
        tile_belowEast = self.getBelowEastTile()
        tile_belowNorth = self.getBelowNorthTile()
        tile_belowSouth = self.getBelowSouthTile()
        
        tile_belowNorthWest = self.getBelowNorthWestTile()
        tile_belowNorthEast = self.getBelowNorthEastTile()
        tile_belowSouthWest = self.getBelowSouthWestTile()
        tile_belowSouthEast = self.getBelowSouthEastTile()
        
        tile_aboveWest = self.getAboveWestTile()
        tile_aboveEast = self.getAboveEastTile()
        tile_aboveNorth = self.getAboveNorthTile()
        tile_aboveSouth = self.getAboveSouthTile()
        
        tile_aboveNorthWest = self.getAboveNorthWestTile()
        tile_aboveNorthEast = self.getAboveNorthEastTile()
        tile_aboveSouthWest = self.getAboveSouthWestTile()
        tile_aboveSouthEast = self.getAboveSouthEastTile()
        
        tile_neighbour_list.append(tile_west)
        tile_neighbour_list.append(tile_east)
        tile_neighbour_list.append(tile_north)
        tile_neighbour_list.append(tile_south)
        
        tile_neighbour_list.append(tile_northWest)
        tile_neighbour_list.append(tile_northEast)
        tile_neighbour_list.append(tile_southWest)
        tile_neighbour_list.append(tile_southEast)
        
        tile_neighbour_list.append(tile_belowWest)
        tile_neighbour_list.append(tile_belowEast)
        tile_neighbour_list.append(tile_belowNorth)
        tile_neighbour_list.append(tile_belowSouth)
        
        tile_neighbour_list.append(tile_belowNorthWest)
        tile_neighbour_list.append(tile_belowNorthEast)
        tile_neighbour_list.append(tile_belowSouthWest)
        tile_neighbour_list.append(tile_belowSouthEast)

        tile_neighbour_list.append(tile_aboveWest)
        tile_neighbour_list.append(tile_aboveEast)
        tile_neighbour_list.append(tile_aboveNorth)
        tile_neighbour_list.append(tile_aboveSouth)
        
        tile_neighbour_list.append(tile_aboveNorthWest)
        tile_neighbour_list.append(tile_aboveNorthEast)
        tile_neighbour_list.append(tile_aboveSouthWest)
        tile_neighbour_list.append(tile_aboveSouthEast)
        
        return tile_neighbour_list            
        
        
        
    def getCorner(self):
        ## first move right , and move left == the last 32-level set to zero 
        ## still 32 bits
        corner_lCode = self.coord.getLng().getCode() >> (32 - self.level) << (32 - self.level)
        corner_bCode = self.coord.getLat().getCode() >> (32 - self.level) << (32 - self.level)
        corner_hCode = self.coord.getHei().getCode() >> (32 - self.level) << (32 - self.level)
        corner = LngLat3D(corner_lCode, corner_bCode, corner_hCode, self.level);
        return corner
    
    
    
    def add_pt_label(self, pt_label):
        if str(pt_label) in self.label_dict:
            old_count = self.label_dict[str(pt_label)]
            self.label_dict[str(pt_label)] = old_count + 1
        else: 
            self.label_dict[str(pt_label)] = 1
        
    
    
    def getConnectNeighbours(self):
        return self.connected_neighbours
    
    def __str__(self):
        code = self.code;
        output4 = "G"
        for i in range(31, 31 - self.level, -1):
            v = (code >> i * 3) & 0x7;
            output4= output4 + str(v);
            if (i > 32 - self.level):
                if (i == 23 or i == 17):
                    output4= output4 +"-";
                if (i == 11):
                    output4= output4 +".";
        return output4;

