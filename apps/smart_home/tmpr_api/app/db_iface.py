import os
import psycopg2
import random
import json

__db_iface = None

SENSOR_DB_STORAGE = "sensors"

SNSR_ATTR_ID   = "id"   # int
SNSR_ATTR_NAME = "name" # VARCHAR(100)
SNSR_ATTR_TYOE = "type" # VARCHAR(50)
SNSR_ATTR_LOC  = "location" # VARCHAR(100)
SNSR_ATTR_VAL  = "value" # FLOAT
SNSR_ATTR_UNT  = "unit" # VARCHAR(20)
SNSR_ATTR_STS  = "status" # VARCHAR(20)
SNSR_ATTR_UPDT = "last_updated" # TIMESTAMP
SNSR_ATTR_CRTD = "created_at" # TIMESTAMP

MAX_TEMPERATURE = 60.0

# -----------------------------------------------------------------------------------------------
# Sensor API data interface
# -----------------------------------------------------------------------------------------------
def get_sensor_state(id):
    sensor_data = read_from_db(SENSOR_DB_STORAGE, [SNSR_ATTR_VAL, SNSR_ATTR_STS], id)
    result = sensor_data

    if sensor_data and (len(sensor_data) == 1):
        result = { SNSR_ATTR_VAL : sensor_data[0][0], 
                   SNSR_ATTR_STS : sensor_data[0][1]}
        
        refresh_sensor_value(id)
    
    return result

# -----------------------------------------------------------------------------------------------
def refresh_sensor_value(id):
    return update_sensor_data({SNSR_ATTR_ID : id, SNSR_ATTR_VAL : random.uniform(-MAX_TEMPERATURE, MAX_TEMPERATURE)})

# -----------------------------------------------------------------------------------------------
def update_sensor_data(snsr_description):
    result = None

    if snsr_description and (SNSR_ATTR_ID in snsr_description):
        result = update_db_rec(snsr_description.pop(SNSR_ATTR_ID), SENSOR_DB_STORAGE, snsr_description)         

    return result

# -----------------------------------------------------------------------------------------------
def delete_sensor(id):
    return delete_db_rec(id, SENSOR_DB_STORAGE)

# -----------------------------------------------------------------------------------------------
def get_sensors_list():
    return read_from_db(SENSOR_DB_STORAGE)

# -----------------------------------------------------------------------------------------------
def add_sensor_data(snsr_description):
    return write_to_db(SENSOR_DB_STORAGE, snsr_description)

# -----------------------------------------------------------------------------------------------
# DBI
# -----------------------------------------------------------------------------------------------
def delete_db_rec(rec_id, storage):
    result = exec_sql_request("DELETE FROM {:s} WHERE {:s}={:d}".format(storage, SNSR_ATTR_ID, rec_id))
    
    if result:
        global __db_iface
        __db_iface.commit()
        result = "OK"

    return result

# -----------------------------------------------------------------------------------------------
def format_db_field(k, v):
    return "{:s}={:s}".format(k, str(format_df_by_type(v)))

# -----------------------------------------------------------------------------------------------
def format_df_by_type(v):
    if type(v) is str:
        v = "'{:s}'".format(v)
    return v

# -----------------------------------------------------------------------------------------------
def update_db_rec(rec_id, storage, data):
    result = None
    cond = ""

    if rec_id:
        cond = " WHERE {:s}={:d}".format(SNSR_ATTR_ID, rec_id)
 
    if exec_sql_request("UPDATE {:s} SET {:s}{:s}".
                        format(storage, ", ".join([format_db_field(k,v) for k,v in data.items()]), cond)):
        global __db_iface
        __db_iface.commit()
        result = "OK"

    return result

# -----------------------------------------------------------------------------------------------
def write_to_db(storage, dr):
    result = None

    if dr:
        global __db_iface

        if exec_sql_request("INSERT INTO {:s} ({:s}) VALUES ({:s})".
                            format(storage, ", ".join(list(dr.keys())), 
                                            ", ".join([format_df_by_type(v) for k,v in dr.items()]))):
            __db_iface.commit()
            result = "OK"

    return result

# -----------------------------------------------------------------------------------------------
def read_from_db(storage, what = None, id = None):
    read_cmd = "SELECT {:s} FROM {:s}{:s}"
    cond = ""
    whatData = ""

    if id:
        cond = " WHERE {:s}={:d}".format(SNSR_ATTR_ID, id)
    
    if what is None:
        whatData = "*"
    else:
        whatData = ", ".join(what)

    result = exec_sql_request(read_cmd.format(whatData, storage, cond))

    if result:
        result = result.fetchall()

    return result

# -----------------------------------------------------------------------------------------------
def exec_sql_request(sql_rqst):
    result = None

    try:
        global __db_iface

        print("SQL >> " + sql_rqst)
        
        if is_db_ready():
            c = __db_iface.cursor()
            c.execute(sql_rqst)
            result = c
                            
    except Exception as e:
        print("DBI error: " + str(e))

    return result

# ----------------------------------------------------------------------------------------------
def init_db():
    try:
        global __db_iface
        
        __db_iface = psycopg2.connect(host='localhost',
                                  database=os.environ.get('POSTGRES_DB'),
                                  user=os.environ.get('POSTGRES_USER'),
                                  password=os.environ.get('POSTGRES_PASSWORD'))                                      
        print("Db connected!")                              
    except Exception as e:
        print("Db initialization faild: " + str(e))

# -----------------------------------------------------------------------------------------------
def is_db_ready():
    return __db_iface is not None 