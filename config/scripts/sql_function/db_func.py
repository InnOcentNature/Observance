import datetime
import logging
import mysql.connector

logger = logging.getLogger(__name__)


# Establish database connection
def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Zeshaan7.@",
            database="observance_db",
        )
        return connection
    except Exception as err:
        logger.error(" error", exc_info=True)


# ------------- functions used in mqtt_data.py file ---------------#

# Fetch all gwId and lastUpdateTime from dcu_status
def get_all_gw_epoch(conn):
    try:
        sql = "SELECT gwId, timestamp from dcu_status"
        cursor = conn.cursor()
        cursor.execute(sql)
        gw_epoch_list = cursor.fetchall()
        cursor.close()
        conn.close()
        logger.info("Connection closed")
        return gw_epoch_list
    except Exception as err:
        logger.error(f"{err}", exc_info=True)
    finally:
        if conn.is_connected():
            conn.close()


# Fetch all nodeId and lastUpdateTime from dcu_node_mapping
def get_all_node_epoch(conn):
    try:
        sql = "SELECT nodeId, timestamp from dcu_node_mapping"
        cursor = conn.cursor()
        cursor.execute(sql)
        node_epoch_list = cursor.fetchall()
        cursor.close()
        conn.close()
        logger.info("Connection closed")
        return node_epoch_list
    except Exception as err:
        logger.error(f"{err}", exc_info=True)
    finally:
        if conn.is_connected():
            conn.close()


#  Fetch all nodeId and gwId from dcu_node_mapping table
def get_all_node_gw(conn):
    try:
        sql = "SELECT nodeId, gwId from dcu_node_mapping"
        cursor = conn.cursor()
        cursor.execute(sql)
        node_gw_list = cursor.fetchall()
        cursor.close()
        conn.close()
        logger.info("Connection closed")
        return node_gw_list
    except Exception as err:
        logger.error(f"{err}", exc_info=True)
    finally:
        if conn.is_connected():
            conn.close()


#  Inserting new dcu or Updating existing dcu in dcu_status table
def insert_update_gw(conn, row):
    cursor = None
    try:
        gwId = int(row[0])
        timestamp = int(row[1])
        debugServerTime = datetime.datetime.fromtimestamp(timestamp / 1000)
        sql = "SELECT gwId, timestamp, debugServerTime FROM dcu_status WHERE gwId = %s"
        val = (gwId,)
        cursor = conn.cursor()
        cursor.execute(sql, val)
        gw_row = cursor.fetchone()
        log_msg = ""
        if gw_row is None:
            last_update_time = debugServerTime
            sql = """
                    INSERT INTO dcu_status (gwId,timestamp,debugServerTime,last_update_time) VALUES (%s,%s,%s,%s)
                """
            val = (gwId, timestamp, debugServerTime, last_update_time)
            cursor.execute(sql, val)
            conn.commit()
            log_msg = f" New Row inserted : {row}"
        else:
            last_update_time = gw_row[2]
            sql = """
                    UPDATE dcu_status SET timestamp=%s, debugServerTime=%s, last_update_time=%s WHERE gwId=%s
                """
            val = (timestamp, debugServerTime, last_update_time, gwId)
            cursor.execute(sql, val)
            conn.commit()
            log_msg = f" Row {gw_row} Updated after 30 min : {row} "
        cursor.close()
        conn.close()
        # logger.info(f" G : Connection closed : {log_msg}")
    except Exception as err:
        logger.error(" error", exc_info=True)
    finally:
        if conn.is_connected():
            conn.close()


# Inserting new nodeId or Updating existing nodeId in dcu_node_mapping table
def insert_update_node(conn, row):
    cursor = None
    try:
        # (nodeId, gwId, sinkId, sinkNo, epochtime)
        nodeId = int(row[0])
        gwId = int(row[1])
        sinkId = str(row[2])
        sinkNo = int(row[3])
        timestamp = int(row[4])
        debugServerTime = datetime.datetime.fromtimestamp(timestamp / 1000)
        sql = "SELECT nodeId, gwId, timestamp, debugServerTime FROM dcu_node_mapping WHERE nodeId = %s"
        val = (nodeId,)
        cursor = conn.cursor()
        cursor.execute(sql, val)
        node_row = cursor.fetchone()
        log_msg = "Connected"
        if node_row is None:
            last_update_time = debugServerTime
            sql = """
                INSERT INTO dcu_node_mapping (nodeId,gwId,sinkId,sinkNo,timestamp,debugServerTime,last_update_time)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """
            val = (nodeId, gwId, sinkId, sinkNo, timestamp, debugServerTime, last_update_time)
            cursor.execute(sql, val)
            conn.commit()
            log_msg = f"{log_msg} : New Row inserted : {row}"
        else:
            last_update_time = node_row[3]
            sql = """
                UPDATE dcu_node_mapping SET gwId=%s, sinkId=%s, sinkNo=%s, timestamp=%s, debugServerTime=%s, last_update_time=%s
                WHERE nodeId=%s
            """
            val = (gwId, sinkId, sinkNo, timestamp, debugServerTime, last_update_time, nodeId)
            cursor.execute(sql, val)
            conn.commit()
            log_msg = f"{log_msg} : Previous {node_row} Row updated after 30 min : {row}"
        cursor.close()
        conn.close()
        # logger.info(f"N : {log_msg} : Connection closed")
    except Exception as err:
        logger.error(" error", exc_info=True)
    finally:
        if conn.is_connected():
            conn.close()


# ------------- functions used in kafka_data.py file ---------------#

#  Fetch all nodeId and meterNumber from meter_node_mapping table
def get_all_meter_node(conn):
    try:
        sql = "SELECT nodeId, meterNumber from meter_node_mapping"
        cursor = conn.cursor()
        cursor.execute(sql)
        meter_node = cursor.fetchall()
        cursor.close()
        conn.close()
        logger.info("Connection closed")
        return meter_node
    except Exception as err:
        logger.error(f"{err}", exc_info=True)
    finally:
        if conn.is_connected():
            conn.close()


#  Fetch all nodeId and lastUpdateTime from meter_node_mapping table
def get_all_node_timestamp(conn):
    try:
        sql = "SELECT nodeId, timestamp from meter_node_mapping"
        cursor = conn.cursor()
        cursor.execute(sql)
        node_timestamp = cursor.fetchall()
        cursor.close()
        conn.close()
        logger.info("Connection closed")
        return node_timestamp
    except Exception as err:
        logger.error(f"{err}", exc_info=True)
    finally:
        if conn.is_connected():
            conn.close()


#  Inserting new nodeId and meterNumber or Updating existing row for the same in meter_node_mapping table
#  Also checking if it is a duplicate entry then inserting it to duplicate_meter_node_mapping table
def insert_update_meter_node(conn, row):
    cursor = None
    try:
        # (nodeId, meterNumber, meterMaker, rfMeterType, timestamp)
        nodeId = int(row[0])
        meterNumber = str(row[1])
        meterMaker = str(row[2])
        rfMeterType = str(row[3])
        timestamp = int(row[4])
        debugServerTime = datetime.datetime.fromtimestamp(timestamp / 1000)
        sql = "SELECT nodeId, meterNumber, debugServerTime FROM meter_node_mapping WHERE nodeId = %s"
        val = (nodeId,)
        cursor = conn.cursor(buffered=True)
        cursor.execute(sql, val)
        meter_node_row = cursor.fetchone()
        log_msg = "Connected"
        if meter_node_row is None:
            sql = "SELECT nodeId, meterNumber FROM meter_node_mapping WHERE meterNumber = %s"
            val = (meterNumber,)
            cursor.execute(sql, val)
            meter_node_row = cursor.fetchone()
            last_update_time = debugServerTime
            if meter_node_row is None:
                sql = """
                    INSERT INTO meter_node_mapping (nodeId,meterNumber,meterMaker,rfMeterType,timestamp,debugServerTime, last_update_time) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                """
                val = (nodeId, meterNumber, meterMaker, rfMeterType, timestamp, debugServerTime, last_update_time)
                cursor.execute(sql, val)
                conn.commit()
                log_msg = f"{log_msg} : New Row inserted in MeterNode : {row}"
            else:
                existingNode = int(meter_node_row[0])
                sql = "SELECT nodeId, meterNumber, existingMeterNumber, debugServerTime FROM duplicate_meter_node_mapping WHERE nodeId = %s"
                val = (nodeId,)
                cursor.execute(sql, val)
                duplicate_meter_node_row = cursor.fetchone()
                if duplicate_meter_node_row is None:
                    last_update_time = debugServerTime
                    sql = """
                    INSERT INTO duplicate_meter_node_mapping (nodeId,meterNumber,meterMaker,rfMeterType,timestamp,debugServerTime, existingMeterNumber, last_update_time) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """
                    val = (nodeId, meterNumber, meterMaker, rfMeterType, timestamp, debugServerTime, existingNode, last_update_time)
                    cursor.execute(sql, val)
                    conn.commit()
                    log_msg = f"{log_msg} : New Row inserted in duplicate_meter_node_mapping {row} against : {meter_node_row}"
                else:
                    saved_duplicate_meter = duplicate_meter_node_row[1]
                    last_update_time = duplicate_meter_node_row[3]
                    if str(saved_duplicate_meter) == meterNumber:
                        sql = """
                            UPDATE duplicate_meter_node_mapping SET timestamp=%s, debugServerTime=%s, last_update_time=%s WHERE nodeId=%s
                        """
                        val = (timestamp, debugServerTime, last_update_time, nodeId)
                        cursor.execute(sql, val)
                        conn.commit()
                        log_msg = f"{log_msg} : Row updated in duplicate_meter_node_mapping from {duplicate_meter_node_row} to : {row}"
                    else:
                        last_update_time = debugServerTime
                        sql = """
                        INSERT INTO duplicate_meter_node_mapping (nodeId,meterNumber,meterMaker,rfMeterType,timestamp,debugServerTime, existingMeterNumber, last_update_time) 
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        """
                        val = (
                            nodeId, meterNumber, meterMaker, rfMeterType, timestamp, debugServerTime,
                            existingNode, last_update_time)
                        cursor.execute(sql, val)
                        conn.commit()
                        log_msg = f"{log_msg} : New row inserted due to meterNumber mismatch in duplicate_meter_node_mapping {row} : existing node row {duplicate_meter_node_row}"
        else:
            if meter_node_row[1] == meterNumber:
                last_update_time = meter_node_row[2]
                sql = """
                    UPDATE meter_node_mapping SET timestamp=%s, debugServerTime=%s, last_update_time=%s WHERE nodeId=%s
                """
                val = (timestamp, debugServerTime, last_update_time, nodeId)
                cursor.execute(sql, val)
                conn.commit()
                log_msg = f"{log_msg} : Row updated in MeterNode from {meter_node_row} to : {row}"
            else:
                existingMeterNumber = str(meter_node_row[1])
                sql = "SELECT nodeId, meterNumber, existingMeterNumber, debugServerTime FROM duplicate_meter_node_mapping WHERE nodeId = %s"
                val = (nodeId,)
                cursor.execute(sql, val)
                conn.commit()
                duplicate_meter_node_row = cursor.fetchone()
                if duplicate_meter_node_row is None:
                    last_update_time = debugServerTime
                    sql = """
                        INSERT INTO duplicate_meter_node_mapping (nodeId,meterNumber,meterMaker,rfMeterType,timestamp,debugServerTime, existingMeterNumber, last_update_time) 
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """
                    val = (
                        nodeId, meterNumber, meterMaker, rfMeterType, timestamp, debugServerTime, existingMeterNumber,
                        last_update_time)
                    cursor.execute(sql, val)
                    conn.commit()
                    log_msg = f"{log_msg} : New Row inserted in duplicate_meter_node_mapping {row} against : {meter_node_row}"
                else:
                    saved_duplicate_meter = duplicate_meter_node_row[1]
                    last_update_time = duplicate_meter_node_row[3]
                    if str(saved_duplicate_meter) == meterNumber:
                        sql = """
                            UPDATE duplicate_meter_node_mapping SET timestamp=%s, debugServerTime=%s, last_update_time=%s WHERE nodeId=%s
                        """
                        val = (timestamp, debugServerTime, last_update_time, nodeId)
                        cursor.execute(sql, val)
                        conn.commit()
                        log_msg = f"{log_msg} : Row updated in duplicate_meter_node_mapping from {duplicate_meter_node_row} to : {row}"
                    else:
                        last_update_time = debugServerTime
                        sql = """
                            INSERT INTO duplicate_meter_node_mapping (nodeId,meterNumber,meterMaker,rfMeterType,timestamp,debugServerTime, existingMeterNumber, last_update_time) 
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        """
                        val = (
                            nodeId, meterNumber, meterMaker, rfMeterType, timestamp, debugServerTime,
                            existingMeterNumber, last_update_time)
                        cursor.execute(sql, val)
                        conn.commit()
                        log_msg = f"{log_msg} : New row inserted due to meterNumber mismatch in duplicate_meter_node_mapping {row} : existing node row {duplicate_meter_node_row}"
        cursor.close()
        conn.close()
        # logger.info(f"M : {log_msg} : Connection closed")
    except Exception as err:
        logger.error(f"error : {row}", exc_info=True)
