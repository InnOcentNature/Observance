from django.db import models

# Create your models here.


class Dcu(models.Model):
    gwId = models.BigIntegerField(unique=True, error_messages={'unique: gwId already present'})
    timestamp = models.BigIntegerField()
    debugServerTime = models.DateTimeField()
    last_update_time = models.DateTimeField(blank=True)

    class Meta:
        db_table = "dcu_status"


class DcuNode(models.Model):
    nodeId = models.IntegerField(unique=True, error_messages={'unique: nodeId already present'})
    gwId = models.BigIntegerField()
    sinkId = models.CharField(max_length=10)
    sinkNo = models.IntegerField()
    timestamp = models.BigIntegerField()
    debugServerTime = models.DateTimeField()
    last_update_time = models.DateTimeField(blank=True)

    class Meta:
        db_table = "dcu_node_mapping"


class MeterNode(models.Model):
    nodeId = models.IntegerField(unique=True)
    meterNumber = models.CharField(max_length=20, unique=True)
    meterMaker = models.CharField(max_length=50)
    rfMeterType = models.CharField(max_length=20, blank=True)
    timestamp = models.BigIntegerField()
    debugServerTime = models.DateTimeField()
    last_update_time = models.DateTimeField(blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=('nodeId', 'meterNumber',), name='Unique_nodeId_meterNumber')]
        db_table = "meter_node_mapping"


class DuplicateMeterNode(models.Model):
    nodeId = models.IntegerField()
    meterNumber = models.CharField(max_length=20)
    existingMeterNumber = models.CharField(max_length=20)
    meterMaker = models.CharField(max_length=50)
    rfMeterType = models.CharField(max_length=20, blank=True)
    timestamp = models.BigIntegerField()
    debugServerTime = models.DateTimeField()
    last_update_time = models.DateTimeField(blank=True)

    class Meta:
        db_table = "duplicate_meter_node_mapping"
