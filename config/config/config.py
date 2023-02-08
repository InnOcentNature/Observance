# environment mode 
DEBUG_MODE = False

# Database credentials 
DB_CONFIG = {
	'host': "localhost",
	'port': "3306",
	'user': "root",
	'password': "Zeshaan7.@",
	'db': "observance_db",
}

# MQTT credentials
MQTT_CONFIG = {
	'broker': "nms-wirepass-prod.adanielectricity.com",
	'port': "8883",
	'user': "mqttmasteruser",
	'password': "ENwQRmAOoCKG2QtAqYWNATqWKINU0Z",
}

# Kafka credentials
host = '10.127.4.99'
port = '9092'
KAFKA_CONFIG = {
	'bootstrap_servers': f"{host}:{port}",
}
