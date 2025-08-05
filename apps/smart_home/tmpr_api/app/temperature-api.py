import db_iface
import json
from datetime import datetime 
from flask import Flask, request, jsonify

__app = Flask(__name__)
__current_request = request

API_VESRION = "v1"
ENDPOINT_URI = "/api/{:s}/{:s}"
SENSORS_LIST_EP_URI = ENDPOINT_URI.format(API_VESRION, 'sensors')
SENSOR_EP_URI = ENDPOINT_URI.format(API_VESRION, 'sensors/<int:id>')
SENSOR_SETUP_EP_URI = ENDPOINT_URI.format(API_VESRION, 'sensors/<int:id>/value')

# -----------------------------------------------------------------------------------------------
def format_answer(data):
    res_data = "ERROR"
    if data:
        res_data = data

    return jsonify({"result":res_data})

# -----------------------------------------------------------------------------------------------
@__app.route(SENSOR_EP_URI, methods=['GET'])
def get_sensor(id):
    return format_answer(db_iface.get_sensor_state(id)) 

# -----------------------------------------------------------------------------------------------
@__app.route(SENSORS_LIST_EP_URI, methods=['GET'])
def get_sensors():
    return format_answer(db_iface.get_sensors_list())

# -----------------------------------------------------------------------------------------------
@__app.route(SENSORS_LIST_EP_URI, methods=['POST'])
def create_sensor():
    return format_answer(db_iface.add_sensor_data(json.loads(__current_request.json)))

# -----------------------------------------------------------------------------------------------
@__app.route(SENSOR_EP_URI, methods=['PUT'])
def update_sensor():
    return format_answer(db_iface.update_sensor_data(json.loads(__current_request.json))) 

# -----------------------------------------------------------------------------------------------
@__app.route(SENSOR_EP_URI, methods=['DELETE'])
def delete_sensor(id):
    return format_answer(db_iface.delete_sensor(id)) 

# -----------------------------------------------------------------------------------------------
@__app.route(SENSOR_SETUP_EP_URI, methods=['PATCH'])
def setup_sensor(id, value):
    return format_answer(db_iface.update_sensor_data({db_iface.SNSR_ATTR_ID : id, db_iface.SNSR_ATTR_VAL : value}))

# -----------------------------------------------------------------------------------------------
@__app.route('/health', methods=['GET'])
def is_online():
    cur_app_status = 'OFF_line'

    if db_iface.is_db_ready():
        cur_app_status = 'ON_line'

    return jsonify({"service_state":"at {:s} is {:s}".format(datetime.now().strftime("%H:%M:%S"), cur_app_status)})

# -----------------------------------------------------------------------------------------------
@__app.route('/')
def init_app():
    return 'Temperarture API runned!'

# -----------------------------------------------------------------------------------------------
# Entry point for the Application
if __name__ == '__main__':
    db_iface.init_db()  
    # Запуск сервера обработки запросов - все инициализации делать ДО!!!!
    __app.run(debug=True, port=8081, host='0.0.0.0')
       
