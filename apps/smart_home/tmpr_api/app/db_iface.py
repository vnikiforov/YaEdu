import os
import psycopg2
import random

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
    sensor_data = read_from_db(id)
    current_value = None

    if sensor_data:
        current_value = { SNSR_ATTR_VAL : sensor_data[SNSR_ATTR_VAL], 
                          SNSR_ATTR_STS : sensor_data[SNSR_ATTR_STS] }
        
        refresh_sensor_value(id)
    
    return current_value

# -----------------------------------------------------------------------------------------------
def refresh_sensor_value(id):
    return update_sensor_data(id, {SNSR_ATTR_VAL : random.uniform(-MAX_TEMPERATURE, MAX_TEMPERATURE)})

# -----------------------------------------------------------------------------------------------
def update_sensor_data(snsr_description):
    result = None

    if snsr_description and (SNSR_ATTR_ID in snsr_description):
        result = write_to_db(snsr_description.pop(SNSR_ATTR_ID), SENSOR_DB_STORAGE, snsr_description)         

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
    return exec_sql_request("Removing data")

# -----------------------------------------------------------------------------------------------
def update_db_rec(rec_id, storage, data):
    return exec_sql_request("Updating data")

# -----------------------------------------------------------------------------------------------
def write_to_db(storage, dr):
    result = None

    if dr:
        result = exec_sql_request("Writting data")

    return result

# -----------------------------------------------------------------------------------------------
def read_from_db(storage, id = None):
    return exec_sql_request("Reading data")

# -----------------------------------------------------------------------------------------------
def exec_sql_request(sql_rqst):
    result = None

    if is_db_ready:
        result = "Exec cmd: " + sql_rqst

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