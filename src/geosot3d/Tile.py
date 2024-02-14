'''
Created on 2023年6月24日

@author: Zhiyong Wang
'''

# 1dcode, refer to https://help.supermap.com/iDesktop/zh/tutorial/Visualization/MapSetting/SOTIndexMap
# Gddddddddd-mmmmmm-ssssss.uuuuuuuuuuu 9+6+6+11=32

from src.geosot3d.LngLatSegments import LngLatSegments
from src.geosot3d.Morton2D import Morton2D
from src.geosot3d.CellSize import CellSize
from src.geosot3d.Bbox import Bbox
from src.geosot3d.LngLat import LngLat

class Tile:


    def __init__(self, *args):
        
        self.label = 0
        
        if len(args)==2:
            if isinstance(args[0], str):
                args_str = args[0]
                l = args[1]
                if args_str[0]== "G":
                    code = args[0]
                    self.__init__fromLBcode(code, l)
                else:
                    dms = args[0]
                    self.__init__fromDMS(dms, l)  
            else:
                raise ValueError("argumments only two, but no code and dms!")
                
        elif len(args)==3: 
            x = args[0]
            y = args[1]
            l = args[2]
            self.__init__fromXY(x, y, l)
            
        else: 
            raise ValueError("Tile argumments not correct!")     
        
        
        
    def __init__fromDMS(self, dms, l):
        coord = LngLat(dms);
        self.coord = coord
        self.level = l
        self.corner = self.getCorner() 
    # var 1dCode = "G001110221-021123-021123.02203010012";  

    def __init__fromLBcode(self, code):
        level= 0
        for ele in code:
            if (ele.isdigit()):
                v = Tile.getDecodeChar(ele);
                shift = ((31 - level) * 2);
                id = id | v << shift;
                level = level + 1;
                
        morton = Morton2D();
        morton.magicbitDecoding(id, morton.l, morton.b);
        self.coord = LngLat(morton.l, morton.b)
        self.level = level 
        self.corner = self.getCorner() 
        
    def __init__fromXY(self, x, y, l):
        lngCode = x 
        latCode = y 
        coord = LngLat(lngCode, latCode);
        self.coord = coord
        self.level = l
        self.corner = self.getCorner() 

              
        
    def getCode(self):
        morton = Morton2D();
        L = self.coord.getLng().getCode();
        B = self.coord.getLat().getCode();
        return morton.magicbitCoding(L, B);

        
    def getCoordLngCode(self):
        return self.coord.getLng().getCode();

    def getCoordLatCode(self):
        return self.coord.getLat().getCode();

    def getCoordLat(self):
        _segments = LngLatSegments(self.coord.getLat().getCode(), False)       
        return _segments.getDegree();
        
    def getCoordLng(self):
        _segments = LngLatSegments(self.coord.getLng().getCode(), True)
        return _segments.getDegree();

    
    @staticmethod
    def getDecodeChar(c):
        if (c == '1'):
            return (1).to_bytes(1, 'big');
        if (c == '2'):
            return (2).to_bytes(1, 'big');
        if (c == '3'):
            return (3).to_bytes(1, 'big');  
        return (0).to_bytes(1, 'big');

    def getBbox(self):
        cellSize = CellSize();
        cell = cellSize.getCellSizeInDegree(self.level);
        print("xy = ", self.corner.lng.getCode(), self.corner.lat.getCode())
        trtile_x = ((self.corner.lng.getCode()>> (32 - self.level)) + 1) << (32 - self.level)
        trtile_y = ((self.corner.lat.getCode() >> (32 - self.level)) + 1) << (32 - self.level)
        trtile = Tile(trtile_x, trtile_y, self.level);
        self.bbox = Bbox(west =  min(self.corner.getLng().getDegree(), trtile.corner.getLng().getDegree()),
                south = min(self.corner.getLat().getDegree(), trtile.corner.getLat().getDegree()),
                east =  max(self.corner.getLng().getDegree(), trtile.corner.getLng().getDegree()),
                north = max(self.corner.getLat().getDegree(), trtile.corner.getLat().getDegree()))

        return self.bbox;
    
    
    def __str__(self):
        code = self.getCode();
        output4 = "G"
        # 31 30 29 28 27 26 25 24 23 22 (total=10)
        for i in range(31, 31 - self.level, -1):
            v = (code >> i * 2) & 0x3;
            output4= output4 + str(v);
            if (i > 32 - self.level):
                if (i == 23 or i == 17):
                    output4= output4 +"-";
                if (i == 11):
                    output4=output4+".";
        return output4;


    def getCorner(self):
        ## first move right , and move left == the last 32-level set to zero 
        ## still 32 bits
        corner_lCode = self.coord.getLng().getCode() >> (32 - self.level) << (32 - self.level)
        corner_bCode = self.coord.getLat().getCode() >> (32 - self.level) << (32 - self.level)
        corner = LngLat(corner_lCode, corner_bCode);
        
        return corner
