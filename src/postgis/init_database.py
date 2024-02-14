#-------------------------------------------------------------------------------
# Name:     init_database
# Purpose:  configure the database
#
# Author:      Zhiyong Wang
#
# Created:     12/2023
# Copyright:   (c) Zhiyong 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import src.postgis.utility_fun as uf
import time
import logging
import psycopg2
from src.geosot3d.Bbox import Bbox
import json
from src.geosot3d.Tile3D import Tile3D
import numpy as np
from src.geosot3d.GeoUtilities import GeoUtilities

debug = False
logger = logging.getLogger("vdc_logger")

def init_db(level, srid):
    
    if not uf.create_tables:
        return uf.target_table+'_'+str(level)
    
    cur1, conn1 = uf.connect()
    # drop column if exist and then create route column 
    
    cur1.execute("""drop TABLE if exists """+ uf.target_table+'_'+str(level)+""";""")
    
    
    cur1.execute("""CREATE TABLE """ +uf.target_table+'_'+str(level)+""" (
      id integer primary key,
      geosot_id character(50),
      vox_label integer,
      labels json
     );""")
    
    ## geometry of the source ojbect
    cur1.execute("""
    ALTER TABLE """ +uf.target_table+'_'+str(level)+""" DROP COLUMN IF EXISTS bbox_west;
    ALTER TABLE """ +uf.target_table+'_'+str(level)+""" ADD COLUMN bbox_west double precision;
    
    ALTER TABLE """ +uf.target_table+'_'+str(level)+""" DROP COLUMN IF EXISTS bbox_east;
    ALTER TABLE """ +uf.target_table+'_'+str(level)+""" ADD COLUMN bbox_east double precision;
    
    ALTER TABLE """ +uf.target_table+'_'+str(level)+""" DROP COLUMN IF EXISTS bbox_south;
    ALTER TABLE """ +uf.target_table+'_'+str(level)+""" ADD COLUMN bbox_south double precision;
    
    ALTER TABLE """ +uf.target_table+'_'+str(level)+""" DROP COLUMN IF EXISTS bbox_north;
    ALTER TABLE """ +uf.target_table+'_'+str(level)+""" ADD COLUMN bbox_north double precision;   
    
    ALTER TABLE """ +uf.target_table+'_'+str(level)+""" DROP COLUMN IF EXISTS bbox_low;
    ALTER TABLE """ +uf.target_table+'_'+str(level)+""" ADD COLUMN bbox_low double precision;
    
    ALTER TABLE """ +uf.target_table+'_'+str(level)+""" DROP COLUMN IF EXISTS bbox_high;
    ALTER TABLE """ +uf.target_table+'_'+str(level)+""" ADD COLUMN bbox_high double precision;
    """)
    
    if uf.add_utm_columns:
        
        cur1.execute("""
        ALTER TABLE """ +uf.target_table+'_'+str(level)+""" DROP COLUMN IF EXISTS utm0;
        ALTER TABLE """ +uf.target_table+'_'+str(level)+""" ADD COLUMN utm0 geometry(PointZ,"""+str(srid)+""");
        ALTER TABLE """ +uf.target_table+'_'+str(level)+""" DROP COLUMN IF EXISTS utm1;
        ALTER TABLE """ +uf.target_table+'_'+str(level)+""" ADD COLUMN utm1 geometry(PointZ,"""+str(srid)+""");
        

        ALTER TABLE """ +uf.target_table+'_'+str(level)+""" DROP COLUMN IF EXISTS utm2;
        ALTER TABLE """ +uf.target_table+'_'+str(level)+""" ADD COLUMN utm2 geometry(PointZ,"""+str(srid)+""");
        ALTER TABLE """ +uf.target_table+'_'+str(level)+""" DROP COLUMN IF EXISTS utm3;
        ALTER TABLE """ +uf.target_table+'_'+str(level)+""" ADD COLUMN utm3 geometry(PointZ,"""+str(srid)+""");
    
        ALTER TABLE """ +uf.target_table+'_'+str(level)+""" DROP COLUMN IF EXISTS utm4;
        ALTER TABLE """ +uf.target_table+'_'+str(level)+""" ADD COLUMN utm4 geometry(PointZ,"""+str(srid)+""");
        ALTER TABLE """ +uf.target_table+'_'+str(level)+""" DROP COLUMN IF EXISTS utm5;
        ALTER TABLE """ +uf.target_table+'_'+str(level)+""" ADD COLUMN utm5 geometry(PointZ,"""+str(srid)+""");
        

        ALTER TABLE """ +uf.target_table+'_'+str(level)+""" DROP COLUMN IF EXISTS utm6;
        ALTER TABLE """ +uf.target_table+'_'+str(level)+""" ADD COLUMN utm6 geometry(PointZ,"""+str(srid)+""");
        ALTER TABLE """ +uf.target_table+'_'+str(level)+""" DROP COLUMN IF EXISTS utm7;
        ALTER TABLE """ +uf.target_table+'_'+str(level)+""" ADD COLUMN utm7 geometry(PointZ,"""+str(srid)+""");
        """)

    

    ## copy geometry and id
    conn1.commit()
    cur1.close()
    conn1.close()
    
    return uf.target_table+'_'+str(level)



def update_utm_columns(level, srid):
    
    
    cur1, conn1 = uf.connect()
    cur1.execute("""
    Update """ +uf.target_table+'_'+str(level)+""" SET utm0 = ST_Transform(ST_SetSRID(ST_MakePoint(bbox_west, bbox_south,  bbox_high*1000), 4326), """+str(srid)+""");
    Update """ +uf.target_table+'_'+str(level)+""" SET utm1 = ST_Transform(ST_SetSRID(ST_MakePoint(bbox_east, bbox_south,  bbox_high*1000), 4326), """+str(srid)+""");
    
    Update """ +uf.target_table+'_'+str(level)+""" SET utm2 = ST_Transform(ST_SetSRID(ST_MakePoint(bbox_west, bbox_north,  bbox_high*1000), 4326), """+str(srid)+""");
    Update """ +uf.target_table+'_'+str(level)+""" SET utm3 = ST_Transform(ST_SetSRID(ST_MakePoint(bbox_east, bbox_north,  bbox_high*1000), 4326), """+str(srid)+""");
    
    Update """ +uf.target_table+'_'+str(level)+""" SET utm4 = ST_Transform(ST_SetSRID(ST_MakePoint(bbox_east, bbox_south,  bbox_low*1000), 4326), """+str(srid)+""");
    Update """ +uf.target_table+'_'+str(level)+""" SET utm5 = ST_Transform(ST_SetSRID(ST_MakePoint(bbox_west, bbox_south,  bbox_low*1000), 4326), """+str(srid)+""");
    
    Update """ +uf.target_table+'_'+str(level)+""" SET utm6 = ST_Transform(ST_SetSRID(ST_MakePoint(bbox_east, bbox_north,  bbox_low*1000), 4326), """+str(srid)+""");
    Update """ +uf.target_table+'_'+str(level)+""" SET utm7 = ST_Transform(ST_SetSRID(ST_MakePoint(bbox_west, bbox_north,  bbox_low*1000), 4326), """+str(srid)+"""); 
    """)
    

    ## copy geometry and id
    conn1.commit()
    cur1.close()
    conn1.close()
    
    return 



def dump_to_db(level, id_to_tile):
     
    start_time =time.time()
    tile_all_list = []
    index = 1
    for geosot_id, _tile in id_to_tile.items():
        _label = _tile.label
        bbox = _tile.getBbox()
        tile_one_tuple=() 
        tile_one_tuple = (index, geosot_id, _label, bbox.west, bbox.east, bbox.south, bbox.north, bbox.low, bbox.high) 
        tile_all_list.append(tile_one_tuple)
        index = index + 1 
        
    try:
        cur_update, conn_update = uf.connect()
        cur_update.executemany("Insert into " +uf.target_table+"_"+ str(level) + "(id, geosot_id, vox_label,  bbox_west, bbox_east, bbox_south,   bbox_north, bbox_low, bbox_high) values(%s,%s,%s,  %s,%s,%s,  %s,%s,%s)", tile_all_list)
        conn_update.commit()
    except (Exception, psycopg2.Error) as error:
        print("Failed inserting record into table {}".format(error))
    finally:
        # closing database connection.
        if (conn_update):
            cur_update.close()
            conn_update.close()   
    
    end_time = time.time()
    time_diff = end_time - start_time # in seconds
    print("insert table for ", uf.target_table+'_'+str(level), "; running time = ", (time_diff/60), " mins! ", time_diff, " sec! ", time_diff*1000, " million seconds!")
    logger.info("insert table for "+ uf.target_table+'_'+str(level) + "; running time = " + str((time_diff/60)) + " mins! " + str(time_diff) + " sec! " + str(time_diff*1000) + " million seconds!")  
    
    return uf.target_table+'_'+str(level)





def dump_utm_to_db(level, id_to_tile):
     
    start_time =time.time()
    tile_all_list = []
    index = 1
    for geosot_id, _tile in id_to_tile.items():
        _label = _tile.label
        bbox = _tile.getBbox()
        tile_one_tuple=()
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
        utm0_xyz = (tile_points[0][0], tile_points[0][1], tile_points[0][2]) #tuple of xyz
        utm1_xyz = (tile_points[1][0], tile_points[1][1], tile_points[1][2]) #tuple of xyz
        utm2_xyz = (tile_points[2][0], tile_points[2][1], tile_points[2][2]) #tuple of xyz
        utm3_xyz = (tile_points[3][0], tile_points[3][1], tile_points[3][2]) #tuple of xyz
        utm4_xyz = (tile_points[4][0], tile_points[4][1], tile_points[4][2]) #tuple of xyz
        utm5_xyz = (tile_points[5][0], tile_points[5][1], tile_points[5][2]) #tuple of xyz
        utm6_xyz = (tile_points[6][0], tile_points[6][1], tile_points[6][2]) #tuple of xyz
        utm7_xyz = (tile_points[7][0], tile_points[7][1], tile_points[7][2]) #tuple of xyz
        
        tile_one_tuple = (index, geosot_id, _label, bbox.west, bbox.east, bbox.south, bbox.north, bbox.low, bbox.high) + utm0_xyz + utm1_xyz + utm2_xyz + utm3_xyz + utm4_xyz + utm5_xyz + utm6_xyz + utm7_xyz
        tile_all_list.append(tile_one_tuple)
        index = index + 1 
        
    try:
        cur_update, conn_update = uf.connect()
        cur_update.executemany("Insert into " +uf.target_table+"_"+ str(level) + "(id, geosot_id, label, bbox_west, bbox_east, bbox_south, bbox_north, bbox_low, bbox_high, utm0, utm1, utm2, utm3, utm4, utm5, utm6, utm7) values(%s,%s,%s,  %s,%s,%s,%s,%s,%s, ST_MakePoint(%s,%s,%s), ST_MakePoint(%s,%s,%s), ST_MakePoint(%s,%s,%s), ST_MakePoint(%s,%s,%s), ST_MakePoint(%s,%s,%s), ST_MakePoint(%s,%s,%s), ST_MakePoint(%s,%s,%s), ST_MakePoint(%s,%s,%s))", tile_all_list)
        conn_update.commit()
    except (Exception, psycopg2.Error) as error:
        print("Failed inserting record into table {}".format(error))
    finally:
        # closing database connection.
        if (conn_update):
            cur_update.close()
            conn_update.close()   
    
    end_time = time.time()
    time_diff = end_time - start_time # in seconds
    print("insert table for ", uf.target_table+'_'+str(level), "; running time = ", (time_diff/60), " mins! ", time_diff, " sec! ", time_diff*1000, " million seconds!")
    logger.info("insert table for "+ uf.target_table+'_'+str(level) + "; running time = " + str((time_diff/60)) + " mins! " + str(time_diff) + " sec! " + str(time_diff*1000) + " million seconds!")  
    
    return uf.target_table+'_'+str(level)



def getOffsetFromDB(level):
    cur, conn = uf.connect() 
    cur.execute("""select min(st_x(utm0)), max(st_x(utm0)), min(st_y(utm0)), max(st_y(utm0)), min(st_z(utm0)), max(st_z(utm0)) from """ + uf.target_table+'_'+str(level)+";" )
    record_result_set = cur.fetchall()  
    result = record_result_set[0]
    min_x = result[0]
    max_x = result[1]
    min_y = result[2]
    max_y = result[3]
    min_z = result[4]
    max_z = result[5]
    offset = [(min_x+max_x)/2, (min_y+max_y)/2, (min_z+max_z)/2]
    conn.commit()
    cur.close()
    conn.close()
    return offset

def buildWholeSpaceFromDB(level):
    id_to_tile={}
    cur, conn = uf.connect() 
    cur.execute("""select id, geosot_id, vox_label, st_x(utm0), st_y(utm0), st_z(utm0),  st_x(utm1), st_y(utm1), st_z(utm1), st_x(utm2), st_y(utm2), st_z(utm2), st_x(utm3), st_y(utm3), st_z(utm3), st_x(utm4), st_y(utm4), st_z(utm4), st_x(utm5), st_y(utm5), st_z(utm5), st_x(utm6), st_y(utm6), st_z(utm6), st_x(utm7), st_y(utm7), st_z(utm7) from """ + uf.target_table+'_'+str(level)+";" )
    record_result_set = cur.fetchall()  
    st =time.time()
    row_index = 0 
    for row in record_result_set:
        
        #if(row_index%10000==0):
        #    print ("has fetched ", row_index)
        
        row_index = row_index + 1
        _id = row[0]
        geosot_id = row[1]
        vox_label = row[2]
        
        utm0_x = row[3]
        utm0_y = row[4]
        utm0_z = row[5]
        
        utm1_x = row[6]
        utm1_y = row[7]
        utm1_z = row[8]
        
        utm2_x = row[9]
        utm2_y = row[10]
        utm2_z = row[11]
        
        utm3_x = row[12]
        utm3_y = row[13]
        utm3_z = row[14]
        
        utm4_x = row[15]
        utm4_y = row[16]
        utm4_z = row[17]
        
        utm5_x = row[18]
        utm5_y = row[19]
        utm5_z = row[20]
        
        utm6_x = row[21]
        utm6_y = row[22]
        utm6_z = row[23]
        
        utm7_x = row[24]
        utm7_y = row[25]
        utm7_z = row[26]
        
        _3dtile = Tile3D(geosot_id);
        _3dtile.label = vox_label
        _3dtile.setUTMBbox([utm0_x,utm0_y,utm0_z], [utm1_x,utm1_y,utm1_z], [utm2_x,utm2_y,utm2_z], [utm3_x,utm3_y,utm3_z], [utm4_x,utm4_y,utm4_z], [utm5_x,utm5_y,utm5_z], [utm6_x,utm6_y,utm6_z], [utm7_x,utm7_y,utm7_z])
        id_to_tile[geosot_id.strip()] =  _3dtile
        if _id == 521080 and debug: 
            print("row_index = ", row_index, "_3dtile = ", _3dtile, geosot_id, geosot_id.strip()=='G210210203-222013-221023.162362')
    et = time.time()
    elapsed_time = et - st
    print('Execution time for building ' + str(row_index) +' Tiles from DB:', elapsed_time, 'seconds')        
    conn.commit()
    cur.close()
    conn.close()
    return id_to_tile



def buildPointTilesFromDB(level):
    point_to_tile={}
    cur, conn = uf.connect() 
    #cur.execute("""select id, geosot_id, vox_label, st_x(utm0), st_y(utm0), st_z(utm0),  st_x(utm1), st_y(utm1), st_z(utm1), st_x(utm2), st_y(utm2), st_z(utm2), st_x(utm3), st_y(utm3), st_z(utm3), st_x(utm4), st_y(utm4), st_z(utm4), st_x(utm5), st_y(utm5), st_z(utm5), st_x(utm6), st_y(utm6), st_z(utm6), st_x(utm7), st_y(utm7), st_z(utm7) from """ + uf.target_table+'_'+str(level)+" where vox_label >0;" )
    cur.execute("""select id, geosot_id, vox_label, st_x(utm0), st_y(utm0), st_z(utm0),  st_x(utm1), st_y(utm1), st_z(utm1), st_x(utm2), st_y(utm2), st_z(utm2), st_x(utm3), st_y(utm3), st_z(utm3), st_x(utm4), st_y(utm4), st_z(utm4), st_x(utm5), st_y(utm5), st_z(utm5), st_x(utm6), st_y(utm6), st_z(utm6), st_x(utm7), st_y(utm7), st_z(utm7), CAST(labels ->> '6.0' as integer) as num, labels from """ + uf.target_table+'_'+str(level)+" where vox_label >0;" )
    #cur.execute("""select id, geosot_id, vox_label, st_x(utm0), st_y(utm0), st_z(utm0),  st_x(utm1), st_y(utm1), st_z(utm1), st_x(utm2), st_y(utm2), st_z(utm2), st_x(utm3), st_y(utm3), st_z(utm3), st_x(utm4), st_y(utm4), st_z(utm4), st_x(utm5), st_y(utm5), st_z(utm5), st_x(utm6), st_y(utm6), st_z(utm6), st_x(utm7), st_y(utm7), st_z(utm7), CAST(labels ->> '6.0' as integer) as num, labels from """ + uf.target_table+'_'+str(level)+" where vox_label >0 and st_contains (ST_MakePolygon(ST_GeomFromText('LINESTRING(328857.55 5796324.16, 328879.29 5796363.52, 328862.0 5796368.6, 328845.1 5796334.1, 328857.55 5796324.16)', 32755)), utm0);" )
    #cur.execute("""select id, geosot_id, vox_label, st_x(utm0), st_y(utm0), st_z(utm0),  st_x(utm1), st_y(utm1), st_z(utm1), st_x(utm2), st_y(utm2), st_z(utm2), st_x(utm3), st_y(utm3), st_z(utm3), st_x(utm4), st_y(utm4), st_z(utm4), st_x(utm5), st_y(utm5), st_z(utm5), st_x(utm6), st_y(utm6), st_z(utm6), st_x(utm7), st_y(utm7), st_z(utm7) from """ + uf.target_table+'_'+str(level)+" where id = 58512 or id = 58513 or id = 86072;" )
    record_result_set = cur.fetchall()  
    st =time.time()
    row_index = 0 
    for row in record_result_set:
     
        #if(row_index%10000==0):
        #    print ("has fetched ", row_index)
        
        row_index = row_index + 1
        _id = row[0]
        geosot_id = row[1]
        vox_label = row[2]
        if debug: 
            print("id = ", row)
            print("id = ", row[24], row[25], row[26])
        
        utm0_x = row[3]
        utm0_y = row[4]
        utm0_z = row[5]
        
        utm1_x = row[6]
        utm1_y = row[7]
        utm1_z = row[8]
        
        utm2_x = row[9]
        utm2_y = row[10]
        utm2_z = row[11]
        
        utm3_x = row[12]
        utm3_y = row[13]
        utm3_z = row[14]
        
        utm4_x = row[15]
        utm4_y = row[16]
        utm4_z = row[17]
        
        utm5_x = row[18]
        utm5_y = row[19]
        utm5_z = row[20]
        
        utm6_x = row[21]
        utm6_y = row[22]
        utm6_z = row[23]
        
        utm7_x = row[24]
        utm7_y = row[25]
        utm7_z = row[26]
        
        num = row[27]
        label_dict = row[28]
        point_sum = sum(label_dict.values())
        if num is not None:
            if point_sum < 300: #500
                continue
        
        _3dtile = Tile3D(geosot_id);
        _3dtile.label = vox_label
        _3dtile.label_dict = label_dict
        _3dtile.setUTMBbox([utm0_x,utm0_y,utm0_z], [utm1_x,utm1_y,utm1_z], [utm2_x,utm2_y,utm2_z], [utm3_x,utm3_y,utm3_z], [utm4_x,utm4_y,utm4_z], [utm5_x,utm5_y,utm5_z], [utm6_x,utm6_y,utm6_z], [utm7_x,utm7_y,utm7_z])
        
        if debug: 
            print("id = ", _id, geosot_id, _3dtile.getUTMBbox().utm7)
        
        point_to_tile[geosot_id.strip()] =  _3dtile
    
    et = time.time()
    elapsed_time = et - st
    print('Execution time for building point tiles from DB:', elapsed_time, ' seconds')        
    conn.commit()
    cur.close()
    conn.close()
    print("The total num of Point Tiles from DB = ", len(point_to_tile))
    return point_to_tile

def update_all_voxel_labels(point_to_tile, level):
    point_label_list = []
    start_time =time.time()
    row_index = 0
    for geosot_id, _tile in point_to_tile.items():
        row_index = row_index + 1        
        lable_one_tuple=()
        _tile.label = int(float(max(_tile.label_dict, key = lambda x:_tile.label_dict[x])))    
        lable_one_tuple = (json.dumps(_tile.label_dict), _tile.label, geosot_id)
        point_label_list.append(lable_one_tuple)
        
        if row_index % uf.batch_number == 0:
            update_vox_label(point_label_list, level)
            end_time = time.time()
            time_diff = end_time - start_time # in seconds
            time_diff = round(time_diff, 2)
            time_diff_min = round(time_diff/60, 2) # in mins
            
            if debug:
                print("update voxels labels ", geosot_id, "row_index = " , row_index, " result= " , lable_one_tuple, "; running time = ", time_diff_min, " mins! ", time_diff, " sec! ")
        
            # empty list
            start_time =time.time()
            point_label_list = []
            
    print("update voxels labels ", geosot_id, "row_index = " , row_index, " result= " , lable_one_tuple, "; running time = ", time_diff_min, " mins! ", time_diff, " sec! ")
    update_vox_label(point_label_list, level)
    


def update_vox_label(point_to_labels, level):
    
    try:
        cur_update, conn_update =uf. connect()
        cur_update.executemany("UPDATE " + uf.target_table+"_"+ str(level) + " SET labels = %s, vox_label = %s where geosot_id = %s;",  
        point_to_labels)
        conn_update.commit()
    except (Exception, psycopg2.Error) as error:
        print("Failed inserting record into table {}".format(error))
    finally:
        # closing database connection.
        if (conn_update):
            cur_update.close()
            conn_update.close()



def add_utm_db(level, id_to_tile):
     
    start_time =time.time()
    tile_all_list = []
    index = 1
    for geosot_id, _tile in id_to_tile.items():
        bbox = _tile.getBbox()
        tile_one_tuple=()
        tile_one_tuple = (index, geosot_id, bbox.west, bbox.east, bbox.south, bbox.north, bbox.low, bbox.high)
        tile_all_list.append(tile_one_tuple)
        index = index + 1 
        
    try:
        cur_update, conn_update = uf.connect()
        cur_update.executemany("Insert into " +uf.target_table+"_"+ str(level) + "(id, geosot_id, bbox_west, bbox_east, bbox_south, bbox_north, bbox_low, bbox_high) values(%s,%s,%s,%s,%s,%s,%s,%s)", tile_all_list)
        conn_update.commit()
    except (Exception, psycopg2.Error) as error:
        print("Failed inserting record into table {}".format(error))
    finally:
        # closing database connection.
        if (conn_update):
            cur_update.close()
            conn_update.close()   
    
    end_time = time.time()
    time_diff = end_time - start_time # in seconds
    print("insert table for ", uf.target_table+'_'+str(level), "; running time = ", (time_diff/60), " mins! ", time_diff, " sec! ", time_diff*1000, " million seconds!")
    logger.info("insert table for "+ uf.target_table+'_'+str(level) + "; running time = " + str((time_diff/60)) + " mins! " + str(time_diff) + " sec! " + str(time_diff*1000) + " million seconds!")  
    
    return uf.target_table+'_'+str(level)

def test1():
    update_utm_columns(25)

def test():   
    level = 27
    id_to_tile = {}
    dms_au1 = "37° 59' 2.88\" S, 145° 4' 17.88\" E";  
    dms_au2 = "37° 58' 1.88\" S, 145° 3' 17.88\" E";  
    
    _tile1 = Tile3D(dms_au1, 23694.168548, 27); 
    _tile2 = Tile3D(dms_au2, 23694.168548, 27);  
    print("_tile1 = ", _tile1)
    print("_tile2 = ", _tile2)
    id_to_tile[_tile1.__str__()] =  _tile1
    id_to_tile[_tile2.__str__()] =  _tile2
    
    init_db(level, 32755)
    dump_to_db(level, id_to_tile)
    
#test()    