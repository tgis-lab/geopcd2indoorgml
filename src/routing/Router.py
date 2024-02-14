'''
Created on 2023年9月5日

@author: Administrator
'''


import networkx as nx
import matplotlib.pyplot as plt

class Router(object):
    
    def __init__(self,  navi_tiles):
        self.navi_tiles = navi_tiles
        return
    
    def export_to_network(self):
        graph = nx.Graph()
        for id, _tile in self.navi_tiles.items():
            
            tile_neighbour_list = []
            
            tile_west = _tile.getWestTile()
            tile_east = _tile.getEastTile()
            tile_north = _tile.getNorthTile()
            tile_south = _tile.getSouthTile()
            
            tile_belowWest = _tile.getBelowWestTile()
            tile_belowEast = _tile.getBelowEastTile()
            tile_belowNorth = _tile.getBelowNorthTile()
            tile_belowSouth = _tile.getBelowSouthTile()
            tile_aboveWest = _tile.getAboveWestTile()
            tile_aboveEast = _tile.getAboveEastTile()
            tile_aboveNorth = _tile.getAboveNorthTile()
            tile_aboveSouth = _tile.getAboveSouthTile()
            
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
            
            for tile_neighbr in tile_neighbour_list:
                if tile_neighbr.__str__() in self.navi_tiles:
                    graph.add_edge(_tile.__str__(), tile_neighbr.__str__(), weight=1)
                    
        nx.draw(graph)
        plt.draw() 
        plt.show()
        print("graph size = ", graph.size())
        return graph
    
    
    def export_to_IndoorGML(self, path_file):
        return