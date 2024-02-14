'''
Created on 2023年9月5日

@author: Administrator
'''
import xml.etree.ElementTree as ET
from xml.dom import minidom
import xml.dom.minidom
import numpy as np
from src.geosot3d.Tile3D import Tile3D
from src.geosot3d.GeoUtilities import GeoUtilities


class XmlWriter(object):
    
    def __init__(self,  navi_tiles):
        self.navi_tiles = navi_tiles
        self.cell_dict = {}
        self.transition_list=[]
        self.state_dict = {}
        self.cell_boundary_list= []
        return
    
    def pretty_print_xml_minidom(self, xml_string):
        # Parse the XML string
        dom = xml.dom.minidom.parseString(xml_string)
        
        # Pretty print the XML
        pretty_xml = dom.toprettyxml(indent="  ")
        
        # Remove empty lines
        pretty_xml = "\n".join(line for line in pretty_xml.split("\n") if line.strip())
        
        # Print the pretty XML
        return pretty_xml

    def prettify(self, xml_str):
        """Return a pretty-printed XML string for the Element.
        """
        reparsed = minidom.parseString(xml_str)
        return reparsed.toprettyxml(indent="  ")

    class TransitionSpace:
        def __init__(self, id, desp, name, _tile):
            self.gml_id = id 
            self.desp = desp
            self.name = name
            self.tile = _tile
            self.hasState = False
            
        def set_state(self, _state):
            self.state = _state
            self.hasState = True 
            
        def has_state(self):
            return self.hasState    
            
        def get_state(self):
            return self.state      
            
        def to_str(self):
            return "TransitionSpace id: " + str(self.gml_id)
    
    class GeneralSpace(object):
        
        def __init__(self, id, desp, name, _tile):
            self.gml_id = id 
            self.desp = desp
            self.name = name
            self.tile = _tile
            self.hasState = False
            
        def to_str(self):
            return "GeneralSpace id: " + str(self.gml_id)
        
        def set_state(self, _state):
            self.state = _state
            self.hasState = True   
            
        def get_state(self):
            return self.state  
                 
        def has_state(self):
            return self.hasState
    
            
    class CellSpaceBoundary:
        def __init__(self, id, desp, name):
            self.gml_id = id 
            self.desp = desp
            self.name = name
            
            
 
 
        def to_str(self):
            return "CellSpaceBoundary id: " + str(self.id)

 

    class State(object):
        def __init__(self, id, desp, name, duality, point):
            self.gml_id = id 
            self.desp = desp
            self.name = name
            self.duality = duality
            self.point = point
 
        def to_str(self):
            return "State id: "+ str(self.gml_id)     
            
    class Transition:
        def __init__(self, id, desp, name, state_from, state_to, duality):
            self.gml_id = id 
            self.desp = desp
            self.name = name
            self.state_from  = state_from
            self.state_to = state_to
            self.duality = duality
            self.points = np.vstack((state_from.point, state_to.point))
            #self.points = np.apply_along_axis(GeoUtilities.wgs_to_utm, 1, self.points)
            
        def to_str(self):
            return "Transition id:"+ self.gml_id

    
    def generate_surface(self, shell, _tile):
        bbox = _tile.getBbox()
        
        tile_points_bbox = np.array([
                [bbox.west, bbox.south, bbox.high],
                [bbox.east, bbox.south, bbox.high],
                [bbox.west, bbox.north, bbox.high],
                [bbox.east, bbox.north, bbox.high],
                [bbox.east, bbox.south, bbox.low],
                [bbox.west, bbox.south, bbox.low],
                [bbox.east, bbox.north, bbox.low],
                [bbox.west, bbox.north, bbox.low],
            ],
            dtype=np.float64,
        )
        #print("tile_points_bbox", tile_points_bbox)
        
        
        tile_points = np.apply_along_axis(GeoUtilities.wgs_to_utm, 1, tile_points_bbox)
        #print("tile_points_bbox = ", tile_points_bbox, " ,tile_points = ", tile_points)
        tile_points_bbox = np.round(tile_points, 3)
        
        tile_triangles = np.array(
            [
                [0, 1, 2, 0],
                [3, 2, 1, 3],
                [1, 0, 4, 1],
                [5, 4, 0, 5],
                [3, 1, 6, 3],
                [4, 6, 1, 4],
                [2, 3, 7, 2],
                [6, 7, 3, 6],
                [0, 2, 5, 0],
                [7, 5, 2, 7],
                [5, 7, 4, 5],
                [6, 4, 7, 6], 
            ],
            dtype="uint32",
            )
        num_triangles, dim_triangles = tile_triangles.shape
        for index_tri in range(num_triangles):
            surfaceMember = ET.SubElement(shell, 'gml:surfaceMember')
            polygon = ET.SubElement(surfaceMember, 'gml:Polygon')
            poly_exterior = ET.SubElement(polygon, 'gml:exterior')
            linearRing = ET.SubElement(poly_exterior, 'gml:LinearRing')
            for index_point in range(len(tile_triangles[index_tri])):
                pos = ET.SubElement(linearRing, 'gml:pos')
                pos.set('srsDimension',"3")
                array = tile_points_bbox[tile_triangles[index_tri]][index_point]
                point_str = str(array[0])+" "+str(array[1])+" "+str(array[2])
                pos.text = point_str
        
        return shell
        
  
    def create_xml_cells(self, cell_dict, sub_root):
        
        primary_features = ET.SubElement(sub_root, 'core:primalSpaceFeatures')
        primary_feature = ET.SubElement(primary_features, 'core:PrimalSpaceFeatures')
        primary_feature.set('gml:id', "PF1")
        primary_feature_boundedBy = ET.SubElement(primary_feature, 'gml:boundedBy')
        primary_feature_boundedBy.set('xsi:nil', "true")
        
        for key, cell in cell_dict.items():
            cellSpaceMember = ET.SubElement(primary_feature_boundedBy, 'core:cellSpaceMember')
            generalSpace = ET.SubElement(cellSpaceMember, 'navi:GeneralSpace')
            #print("cell = " + cell.to_str())
            generalSpace.set('gml:id',str(cell.gml_id))
            desp = ET.SubElement(generalSpace, 'gml:description')
            desp.text = '5.1'
            name = ET.SubElement(generalSpace, 'gml:name')
            name.text = "room"
            boundedBy = ET.SubElement(generalSpace, 'gml:boundedBy')
            boundedBy.set('xsi:nil',"true")
            
            cellSpaceGeometry = ET.SubElement(generalSpace, 'core:cellSpaceGeometry')
            geometry3D = ET.SubElement(cellSpaceGeometry, 'core:Geometry3D')
            solid = ET.SubElement(geometry3D, 'gml:Solid')
            solid.set('gml:id',"CG-C77")
            solid_exterior = ET.SubElement(solid, 'gml:exterior')
            shell = ET.SubElement(solid_exterior, 'gml:Shell')
            self.generate_surface(shell, cell.tile)
            
        return 
    
    
    def create_xml_transitions(self, spaceLayer_boundedBy):
        
        edges = ET.SubElement(spaceLayer_boundedBy, "core:edges")
        edges.set('gml:id', "n9c50278-35ca-adbf-8965-b68be122ca7c")
        edges_boundedBy = ET.SubElement(edges, 'gml:boundedBy')
        edges_boundedBy.set('xsi:nil',"true")
        
        for tran_ele in  self.transition_list:
            transitionMember = ET.SubElement(edges, "core:transitionMember")
            transition = ET.SubElement(transitionMember, "core:Transition")
            transition.set('gml:id', str(tran_ele.gml_id))
            transition_desp = ET.SubElement(transition, "gml:description")
            transition_desp.text = tran_ele.desp
            transition_name = ET.SubElement(transition, "gml:name")
            transition_name.text = tran_ele.name
            transition_boundedBy = ET.SubElement(transition, "gml:boundedBy")
            transition_boundedBy.set('xsi:nil',"true")
            transition_weight = ET.SubElement(transition, "core:weight")
            transition_weight.text = "1.0"
            
            transition_connect = ET.SubElement(transition, "core:connects")
            transition_connect.set('xlink:href',str(tran_ele.state_from.name))
            transition_connect = ET.SubElement(transition, "core:connects")
            transition_connect.set('xlink:href',str(tran_ele.state_from.name))
            transition_duality = ET.SubElement(transition, "core:duality ")
            transition_duality.set('xlink:href',"#B24")
            transition_geom = ET.SubElement(transition, "core:geometry ")
            linearRing = ET.SubElement(transition_geom, 'gml:LinearRing')
            
            for index_point in range(len(tran_ele.points)):
                pos = ET.SubElement(linearRing, 'gml:pos')
                pos.set('srsDimension',"3")
                array = tran_ele.points[index_point]
                #print("tran_ele.points ", index_point, tran_ele.points[index_point])
                point_str = str(array[0])+" "+str(array[1])+" "+str(array[2])
                pos.text = point_str
           
        return


    def create_xml_states(self, spaceLayer_boundedBy):
        nodes = ET.SubElement(spaceLayer_boundedBy, "core:nodes")
        nodes.set('gml:id', "c538cc2a-68f0-ac71-4585-b13f45e656c9")
        nodes_boundedBy = ET.SubElement(nodes, 'gml:boundedBy')
        nodes_boundedBy.set('xsi:nil',"true")
        for key, state_ele in  self.state_dict.items():
            stateMember = ET.SubElement(nodes, "core:stateMember")
            state = ET.SubElement(stateMember, "core:State")
            state.set('gml:id', str(state_ele.gml_id))
            state_desp = ET.SubElement(state, "gml:description")
            state_desp.text = "state desp"
            state_name = ET.SubElement(state, "gml:name")
            state_name.text = state_ele.name
            state_boundedBy = ET.SubElement(state, "gml:boundedBy")
            state_boundedBy.set('xsi:nil',"true")
            state_duality = ET.SubElement(state, "core:duality")
            state_duality.set('xlink:href', "duality")
            state_geom = ET.SubElement(state, "core:geometry ")
            state_point = ET.SubElement(state_geom, 'gml:Point')
            state_point.set('gml:id',str(state_ele.gml_id))
            state_pos = ET.SubElement(state_point, 'gml:pos')
            state_pos.set('srsDimension',"3")
            point_str = str(state_ele.point[0])+" "+str(state_ele.point[1])+" "+str(state_ele.point[2])
            state_pos.text = point_str

 
 
    def create_xml(self, output_path):
        
        self.root = ET.Element('core:IndoorFeatures')
        self.root.set('xmlns:gml', "http://www.opengis.net/gml/3.2")
        self.root.set('xmlns:xlink',"http://www.w3.org/1999/xlink")
        self.root.set('xmlns:core',"http://www.opengis.net/indoorgml/1.0/core") 
        self.root.set('xmlns:navi', "http://www.opengis.net/indoorgml/1.0/navigation")
        self.root.set('xmlns:xsi',"http://www.w3.org/2001/XMLSchema-instance")
        self.root.set('xsi:schemaLocation',"http://www.opengis.net/indoorgml/1.0/core http://schemas.opengis.net/indoorgml/1.0/indoorgmlcore.xsd http://www.opengis.net/indoorgml/1.0/navigation http://schemas.opengis.net/indoorgml/1.0/indoorgmlnavi.xsd")
        self.root.set('gml:id', "a59aa57f-36ab-86fa-8950-d7fa844ab96b")
        
        boundedBy = ET.SubElement(self.root, 'gml:boundedBy')
        boundedBy.set('xsi:nil',"true")
        ## cells 
        self.create_xml_cells(self.cell_dict, boundedBy)


        ## add multilayer graph 
        multi_layer_graphs = ET.SubElement(boundedBy, 'core:multiLayeredGraph')
        multi_layer_graph = ET.SubElement(multi_layer_graphs, 'core:MultiLayeredGraph')
        multi_layer_graph.set('gml:id', "pe0d2dc2-b9fe-3b43-3ded-33449b03f9cc")
        multi_layer_graph_boundedBy = ET.SubElement(multi_layer_graph, 'gml:boundedBy')
        multi_layer_graph_boundedBy.set('xsi:nil', "true")
        
        spaceLayers = ET.SubElement(multi_layer_graph_boundedBy, 'core:spaceLayers')
        spaceLayers.set('gml:id', "j7525157-c860-01ae-b169-0a5ddd7ea42a")
        spaceLayers_boundedBy = ET.SubElement(spaceLayers, "gml:boundedBy")
        spaceLayers_boundedBy.set('xsi:nil', "true")
        spaceLayerMember = ET.SubElement(spaceLayers_boundedBy, 'core:spaceLayerMember')
        SpaceLayer = ET.SubElement(spaceLayerMember, 'core:SpaceLayer')
        SpaceLayer.set('gml:id', "base")
        spaceLayer_boundedBy =  ET.SubElement(SpaceLayer, 'gml:boundedBy')
        spaceLayer_boundedBy.set('xsi:nil', "true")
        
        self.create_xml_states(SpaceLayer)
        self.create_xml_transitions(SpaceLayer)
        
        

        print(ET.tostring(self.root).decode())
        m =  ET.tostring(self.root, encoding="utf-8")
        #print(m)
        pretty_xml =  self.pretty_print_xml_minidom(m)
        #self.prettify(m)
        tree = ET.ElementTree(self.root)
        tree.write(output_path)
        #self.root.write(output_path, encoding ='utf-8', xml_declaration = True)
        with open(output_path, "w") as f:
            f.write(pretty_xml)
    
    
    def generate_cells_from_tiles(self):
        tile_set = self.navi_tiles.copy()
        i = 0 
        for _tile in list(tile_set.values()):
            cell = self.TransitionSpace("C"+str(i), "Transition space", "corridor", _tile)
            self.cell_dict[_tile.__str__()] = cell 
            i = i + 1
        print("The number of cells", i)    
        return 
    
    
    def generate_states_transitions_from_tiles(self):
        
        transition_id = 0
        
        for key, cell in self.cell_dict.items():
            point_x1 = (cell.tile.getBbox().west + cell.tile.getBbox().east)/2 
            point_y1 = (cell.tile.getBbox().south + cell.tile.getBbox().north)/2
            point_z1 = (cell.tile.getBbox().low + cell.tile.getBbox().high)/2 
            point1 = [point_x1, point_y1, point_z1]
            point1 = GeoUtilities.wgs_to_utm(point1)
            #print("point1 = "+ str(point1) + "tile = "+ str(key))
            state= self.State("s"+str(cell.gml_id), "", cell.tile.__str__() ,"", point1)
            cell.set_state(state)
            self.state_dict[state.to_str()]= state
            #print("connected neighbour size " , len(cell.tile.getConnectNeighbours()))
            if len(cell.tile.getConnectNeighbours())==0:
                continue
            for neighbor_tile in cell.tile.getConnectNeighbours():
                neighbor_cell = self.cell_dict[neighbor_tile.__str__()]
                
                if neighbor_cell.has_state() == False:
                    point_x2 = (neighbor_cell.tile.getBbox().west + neighbor_cell.tile.getBbox().east)/2 
                    point_y2 = (neighbor_cell.tile.getBbox().south + neighbor_cell.tile.getBbox().north)/2
                    point_z2 = (neighbor_cell.tile.getBbox().low + neighbor_cell.tile.getBbox().high)/2 
                    point2 = [point_x2, point_y2, point_z2]
                    point2 = GeoUtilities.wgs_to_utm(point2)
                    #print("point1 = "+ str(point1) + ", point 2 = " +str(point2))
                    neighbor_state= self.State("s"+str(neighbor_cell.gml_id), "", neighbor_cell.tile.__str__(), "", point2)
                    neighbor_cell.set_state(neighbor_state)
                    self.state_dict[neighbor_state.to_str()]= neighbor_state
                else:
                    neighbor_state = neighbor_cell.get_state()
                
                #print("state = ",state.to_str(), "neighbor_state = ", neighbor_state.to_str())    
                transition =  self.Transition(str(transition_id), "transition", "tran1", state, neighbor_state, "")
                transition_reverse =  self.Transition(str(transition_id)+"REVERSE", "transition-reverse", "tran1-reverse", neighbor_state, state, "")
                
                self.transition_list.append(transition)  
                self.transition_list.append(transition_reverse)
                transition_id =  transition_id + 1 
        print("The created states number = ", len(self.state_dict), " The created transitions number = ", len(self.transition_list))
        return
        
