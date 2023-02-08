import logging
import threading
import time
from wirepas_mqtt_library import WirepasNetworkInterface
from .sql_function.db_func import *
from config.config import MQTT_CONFIG

logger = logging.getLogger(__name__)

# Helper functions for getting previous records
node_epoch = {}
gw_epoch = {}
node_gw = {}


def get_previous_db_records():
    try:
        while True:
            gw_epoch_list = get_all_gw_epoch(create_db_connection())
            global gw_epoch
            gw_epoch = dict(gw_epoch_list)

            node_epoch_list = get_all_node_epoch(create_db_connection())
            global node_epoch
            node_epoch = dict(node_epoch_list)

            node_gw_list = get_all_node_gw(create_db_connection())
            global node_gw
            node_gw = dict(node_gw_list)

            logger.info("previous records updated : sleeping 30 sec")
            time.sleep(30)
    except Exception as err:
        logger.error(" error", exc_info=True)


def save_node(nodeId, gwId, sinkId, sinkNo, epochtime):
    try:
        row = (nodeId, gwId, sinkId, sinkNo, epochtime)
        conn = create_db_connection()
        insert_update_node(conn, row)
    except Exception as err:
        logger.error(" error", exc_info=True)


def save_gw(gwId, epochtime):
    try:
        row = (gwId, epochtime)
        conn = create_db_connection()
        insert_update_gw(conn, row)
    except Exception as err:
        logger.error(" error", exc_info=True)


def probus_app_data(data):
    try:
        # Checking active thread count
        if threading.active_count() >= 20:
            logger.warning(f" Sleeping for 20 sec : active thread count = {threading.active_count()}")
            time.sleep(20)
            logger.warning(f" active thread count {threading.active_count()}")
        node_Id = f"{data.source_address}"
        gw_Id = f"{data.gw_id}"
        epoch_time = f"{data.rx_time_ms_epoch}"
        gwId = int(gw_Id) if gw_Id.isdecimal() else None
        nodeId = int(node_Id) if node_Id.isdecimal() else None
        epochtime = int(epoch_time) if epoch_time.isdecimal() else None

        if gwId is None or epochtime is None or nodeId is None:
            pass
            # logger.warning(f" Parsing failed for gw_id or epochtime :{data}")
        else:
            # Saving new and Updating existing dcu_table
            if gwId in gw_epoch.keys():
                previous_gw_epoch = gw_epoch[gwId]
                if int(previous_gw_epoch) + 1800000 <= int(epochtime):
                    gw_epoch[gwId] = int(epochtime)
                    save_gw_in_db_thread = threading.Thread(target=save_gw, args=(gwId, epochtime), daemon=True)
                    save_gw_in_db_thread.start()
            else:
                gw_epoch[gwId] = int(epochtime)
                save_gw_in_db_thread = threading.Thread(target=save_gw, args=(gwId, epochtime), daemon=True)
                save_gw_in_db_thread.start()

            sinkId = f"{data.sink_id}"
            sink_No = f"{data.destination_address}"
            sinkNo = int(sink_No) if sink_No.isdecimal() else None

            # Saving new and Updating existing node_table
            if nodeId in node_epoch.keys() and nodeId in node_gw.keys():
                previous_node_epoch = node_epoch[nodeId]
                existing_gw = node_gw[nodeId]
                if int(existing_gw) != gwId:
                    save_node_in_db_thread = threading.Thread(target=save_node, args=(nodeId, gwId, sinkId, sinkNo, epochtime), daemon=True)
                    save_node_in_db_thread.start()
                    node_gw[nodeId] = gwId
                    # logger.info(f"{nodeId} : {existing_gw}  gwId changed to {gwId}")
                else:
                    if int(previous_node_epoch) + 1800000 <= int(epochtime):
                        node_epoch[nodeId] = int(epochtime)
                        save_node_in_db_thread = threading.Thread(target=save_node, args=(nodeId, gwId, sinkId, sinkNo, epochtime), daemon=True)
                        save_node_in_db_thread.start()
            else:
                node_epoch[nodeId] = int(epochtime)
                node_gw[nodeId] = gwId
                save_node_in_db_thread = threading.Thread(target=save_node, args=(nodeId, gwId, sinkId, sinkNo, epochtime), daemon=True)
                save_node_in_db_thread.start()
    except Exception as err:
        logger.error(f"{err}", exc_info=True)


def run():
    try:
        logger.info("MQTT main started")
        # Getting database records
        previous_record_t = threading.Thread(target=get_previous_db_records, daemon=True)
        previous_record_t.start()
        # Connecting to wni mqtt
        wni = WirepasNetworkInterface(MQTT_CONFIG['broker'], MQTT_CONFIG['port'], MQTT_CONFIG['user'],
                                      MQTT_CONFIG['password'])
        # Registering a callback function
        wni.register_data_cb(probus_app_data, network=256)
        while True:
            pass
    except Exception as error:
        logger.error(f"{error}", exc_info=True)