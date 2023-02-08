import logging
import json
import time
import threading
from kafka import KafkaConsumer
from config.config import KAFKA_CONFIG
from .sql_function.db_func import *

logger = logging.getLogger(__name__)

# Helper functions for getting previous records
meter_node = {}
node_timestamp = {}


def get_previous_db_records():
    try:
        while True:
            meter_node_list = get_all_meter_node(create_db_connection())
            global meter_node
            meter_node = dict(meter_node_list)
            # logger.info(" meter node updated : sleeping 30 sec")

            node_timestamp_list = get_all_node_timestamp(create_db_connection())
            global node_timestamp
            node_timestamp = dict(node_timestamp_list)
            logger.info("previous records updated : sleeping 30 sec")
            time.sleep(30)
    except Exception as err:
        logger.error(" error", exc_info=True)


def existing_node_timestamp():
    try:
        while True:
            node_timestamp_list = get_all_node_timestamp(create_db_connection())
            global node_timestamp
            node_timestamp = dict(node_timestamp_list)
            logger.info("node timestamp updated : sleeping 30 sec")
            time.sleep(30)
    except Exception as err:
        logger.error(" error", exc_info=True)


def raw_sensor_data(nodeId, meterNumber, meterMaker, timestamp):
    rfMeterType = ''
    row = (nodeId, meterNumber, meterMaker, rfMeterType, timestamp)
    conn = create_db_connection()
    insert_update_meter_node(conn, row)


def node_init_response(nodeId, meterNumber, meterMaker, rfMeterType, timestamp):
    row = (nodeId, meterNumber, meterMaker, rfMeterType, timestamp)
    conn = create_db_connection()
    insert_update_meter_node(conn, row)


def command_response(message_value):
    pass


def run():
    try:
        logger.info("Calling KAFKA Consumer")
        # Getting database records
        try:
            previous_record_t = threading.Thread(target=get_previous_db_records, daemon=True)
            previous_record_t.start()
        except Exception as err:
            logger.error(f"Error while thread calling : {err}", exc_info=True)

        consumer = KafkaConsumer(bootstrap_servers=KAFKA_CONFIG.get("bootstrap_servers"),
                                 auto_offset_reset="latest",
                                 value_deserializer=lambda m: json.loads(m.decode("utf-8")))
        consumer.subscribe(["raw-sensor-data", "node-init-response"])
        for message in consumer:
            # Checking active thread count
            if threading.active_count() >= 20:
                logger.warning(f" Sleeping for 20 sec : active thread count = {threading.active_count()}")
                time.sleep(20)
                logger.info(f" Active thread count is {threading.active_count()}")

            topic = str(message.topic)
            time_stamp = f"{message.timestamp}"
            timestamp = int(time_stamp) if time_stamp.isdecimal() else None
            if topic == "raw-sensor-data":
                try:
                    if "meterNumber" not in message.value.keys() or len(message.value['meterNumber']) < 5:
                        pass
                        # logger.warning(f"meterNumber key missing : {message.value}")
                    else:
                        if len(message.value['meterNumber']) < 3:
                            logger.info(f"length of meterNumber {len(message.value['meterNumber'])}")
                        nodeId = int(message.value['nodeId'])
                        meterNumber = message.value['meterNumber']
                        meterMaker = message.value['meter_manufacturer']
                        if nodeId in meter_node.keys() and nodeId in node_timestamp.keys():
                            existing_meter = str(meter_node[nodeId])
                            if existing_meter == str(meterNumber):
                                try:
                                    previous_timestamp = int(node_timestamp.get(nodeId))
                                    if previous_timestamp + 1800000 <= timestamp:
                                        node_timestamp[nodeId] = timestamp
                                        raw_sensor_thread = threading.Thread(target=raw_sensor_data, args=(nodeId, meterNumber, meterMaker, timestamp), daemon=True)
                                        raw_sensor_thread.start()
                                except Exception as er:
                                    logger.error("error in raw sensor data topic", exc_info=True)
                            else:
                                logger.warning(f"Duplicate Node Meter found {message.value}")
                                raw_sensor_thread = threading.Thread(target=raw_sensor_data, args=(nodeId, meterNumber, meterMaker, timestamp), daemon=True)
                                raw_sensor_thread.start()
                        else:
                            meter_node[nodeId] = meterNumber
                            raw_sensor_thread = threading.Thread(target=raw_sensor_data, args=(nodeId, meterNumber, meterMaker, timestamp), daemon=True)
                            raw_sensor_thread.start()
                except Exception as err:
                    logger.error(f"error in raw sensor data topic : {message.value} ", exc_info=True)
            elif topic == "node-init-response":
                try:
                    nodeId = int(message.value['nodeId'])
                    meterNumber = message.value['meterNumber']
                    meterMaker = message.value['meterMaker']
                    rfMeterType = message.value['rfMeterType']
                    if meterNumber is None or len(meterNumber) < 5:
                        pass
                        # logger.warning(f"meterNumber is None {message.value}")
                    else:
                        if nodeId in meter_node.keys() and nodeId in node_timestamp.keys():
                            existing_meter = str(meter_node[nodeId])
                            if existing_meter == str(meterNumber):
                                try:
                                    previous_timestamp = int(node_timestamp.get(nodeId))
                                    if previous_timestamp + 1800000 <= timestamp:
                                        node_timestamp[nodeId] = timestamp
                                        node_init_thread = threading.Thread(target=node_init_response, args=(nodeId, meterNumber, meterMaker, rfMeterType, timestamp), daemon=True)
                                        node_init_thread.start()
                                except Exception as er:
                                    logger.error("error in node-init topic", exc_info=True)
                            else:
                                logger.warning(f"Duplicate Node Meter found {message.value}")
                                node_init_thread = threading.Thread(target=node_init_response, args=(nodeId, meterNumber, meterMaker, rfMeterType, timestamp), daemon=True)
                                node_init_thread.start()
                        else:
                            meter_node[nodeId] = meterNumber
                            node_init_thread = threading.Thread(target=node_init_response, args=(nodeId, meterNumber, meterMaker, rfMeterType, timestamp), daemon=True)
                            node_init_thread.start()
                except Exception as err:
                    logger.error(f"error in node-init topic : {message.value} ", exc_info=True)
            elif topic == "command-response":
                pass
    except Exception as err:
        logger.error(f"{err}", exc_info=True)
