#-------------------------------------------------------------------------------
# Name:     utilify_fun
# Purpose:  utility function
#
# Author:      Zhiyong Wang
#
# Created:     12/2023
# Copyright:   (c) Zhiyong 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import logging
import psycopg2



target_table = ''

linux_mode = False
test_mode = False


batch_number = 10
create_tables = True
add_utm_columns = True



def init_logger():
    logger = logging.getLogger("vdc_logger")
    logger.setLevel(logging.INFO)
    if linux_mode:
        logfile = '/home/neil/log/logger.txt'
        #logfile = '/home/zywang/python/log/logger.txt'
    else:
        logfile = 'J://vdc_workspace//vdc//log//logger.txt'
    
    fh = logging.FileHandler(logfile, mode='w')
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)   
    
    
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
        
    logger.addHandler(fh) 
    logger.addHandler(ch)




def connect():
        
    conn = None    
    if linux_mode:
        #conn = psycopg2.connect(database="postgres_nl", user="postgres",host="/var/run/postgresql", password="postgres", port="5432")
        conn = psycopg2.connect(database="postgres_nl", user="zywang",host="/tmp/", password="2203930_ZyW", port="5432")
    else:
        if test_mode:
            conn = psycopg2.connect(database="postgres_test", user="postgres", password="postgres", port="5432")
        else:
            conn = psycopg2.connect(database="postgres_geosot", user="postgres", password="postgres", port="5432")
    
    cur = conn.cursor()
    return cur, conn
