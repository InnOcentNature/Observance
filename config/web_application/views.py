from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from web_application.models import *
from django.db.models import *
import datetime


# Create your views here.


def dashboard(request):
    date_year = datetime.datetime.now().year
    data = {
        "date": date_year
    }
    return render(request, "index.html", data)


# display dcu table
def dcus(request):
    return render(request, 'data_pages/dcu.html')


# load dcu data
def load_dcus(request):
    all_dcus = Dcu.objects.all()

    request_data = request.GET

    draw = int(request_data['draw'])
    length = int(request_data['length'])
    start = int(request_data['start'])

    # filter by gwId
    search_value = request_data['search[value]']
    if search_value:
        search_value = int(search_value) if search_value.isdecimal() else None
        if search_value is None:
            all_dcus = all_dcus.none()
        else:
            all_dcus = all_dcus.filter(gwId__contains=search_value)

    # filter by datetime
    from_time = request_data['from_time']
    till_time = request_data['till_time']
    if from_time and till_time:
        from_time = datetime.datetime.strptime(str(from_time), '%Y-%m-%d %H:%M:%S')
        till_time = datetime.datetime.strptime(str(till_time), '%Y-%m-%d %H:%M:%S')
        all_dcus = all_dcus.filter(debugServerTime__gte=from_time, debugServerTime__lte=till_time)

    sort_column_num = int(request_data['order[0][column]'])
    sort_column = str(request_data[f"columns[{sort_column_num}][name]"])
    sort_column_dir = str(request_data['order[0][dir]'])
    if sort_column_dir == "desc":
        all_dcus = all_dcus.order_by(f"-{sort_column}")
    else:
        all_dcus = all_dcus.order_by(sort_column)
    recordsTotal = len(all_dcus)
    all_dcus = all_dcus[start:start+length]
    data = []
    for dcu in all_dcus:
        data_obj = {
            "gwId": dcu.gwId,
            "timestamp": dcu.timestamp,
            "debugServerTime": dcu.debugServerTime,
            "last_update_time": dcu.last_update_time,
        }
        data.append(data_obj)
    json_data = {
        "draw": draw,
        "recordsFiltered": recordsTotal,
        "recordsTotal": recordsTotal,
        "data": data
    }
    return JsonResponse(json_data)


# display dcu node map table
def dcu_node_mappings(request):
    return render(request, 'data_pages/dcu_node.html')


# load dcu node data
def load_dcu_node_mappings(request):
    dcunode_mappings = DcuNode.objects.all()

    request_data = request.GET

    draw = int(request_data['draw'])
    length = int(request_data['length'])
    start = int(request_data['start'])

    # filter by gwId or nodeId
    search_value = request_data['search[value]']
    if search_value:
        search_value = int(search_value) if search_value.isdecimal() else None
        if search_value is None:
            dcunode_mappings = dcunode_mappings.none()
        else:
            dcunode_mappings = dcunode_mappings.filter(Q(gwId__contains=search_value) | Q(nodeId__contains=search_value))

    # filter by datetime
    from_time = request_data['from_time']
    till_time = request_data['till_time']
    if from_time and till_time:
        from_time = datetime.datetime.strptime(str(from_time), '%Y-%m-%d %H:%M:%S')
        till_time = datetime.datetime.strptime(str(till_time), '%Y-%m-%d %H:%M:%S')
        dcunode_mappings = dcunode_mappings.filter(debugServerTime__gte=from_time, debugServerTime__lte=till_time)

    sort_column_num = int(request_data['order[0][column]'])
    sort_column = str(request_data[f"columns[{sort_column_num}][name]"])
    sort_column_dir = str(request_data['order[0][dir]'])
    if sort_column_dir == "desc":
        dcunode_mappings = dcunode_mappings.order_by(f"-{sort_column}")
    else:
        dcunode_mappings = dcunode_mappings.order_by(sort_column)

    recordsTotal = len(dcunode_mappings)
    dcunode_mappings = dcunode_mappings[start:start + length]
    data = []
    for dcu_node in dcunode_mappings:
        data_obj = {
            "nodeId": dcu_node.nodeId,
            "gwId": dcu_node.gwId,
            "timestamp": dcu_node.timestamp,
            "debugServerTime": dcu_node.debugServerTime,
            "last_update_time": dcu_node.last_update_time,
            "sinkId": dcu_node.sinkId,
            "sinkNo": dcu_node.sinkNo,
        }
        data.append(data_obj)
    json_data = {
        "draw": draw,
        "recordsFiltered": recordsTotal,
        "recordsTotal": recordsTotal,
        "data": data
    }
    return JsonResponse(json_data)


# Display meter node map table
def meter_node_mappings(request):
    return render(request, 'data_pages/meter_node.html')


# Load meter node data
def load_meter_node_mappings(request):
    meternode_mappings = MeterNode.objects.all()

    request_data = request.GET

    draw = int(request_data['draw'])
    length = int(request_data['length'])
    start = int(request_data['start'])

    # filter by meterNumber or nodeId
    search_value = request_data['search[value]']
    if search_value:
        searchvalue = int(search_value) if search_value.isdecimal() else None
        if searchvalue is None:
            meternode_mappings = meternode_mappings.filter(meterNumber__contains=search_value)
        else:
            meternode_mappings = meternode_mappings.filter(Q(nodeId__contains=search_value) | Q(meterNumber__contains=search_value))

    # filter by datetime
    from_time = request_data['from_time']
    till_time = request_data['till_time']
    if from_time and till_time:
        from_time = datetime.datetime.strptime(str(from_time), '%Y-%m-%d %H:%M:%S')
        till_time = datetime.datetime.strptime(str(till_time), '%Y-%m-%d %H:%M:%S')
        meternode_mappings = meternode_mappings.filter(debugServerTime__gte=from_time, debugServerTime__lte=till_time)

    sort_column_num = int(request_data['order[0][column]'])
    sort_column = str(request_data[f"columns[{sort_column_num}][name]"])
    sort_column_dir = str(request_data['order[0][dir]'])
    if sort_column_dir == "desc":
        meternode_mappings = meternode_mappings.order_by(f"-{sort_column}")
    else:
        meternode_mappings = meternode_mappings.order_by(sort_column)

    recordsTotal = len(meternode_mappings)
    meternode_mappings = meternode_mappings[start:start + length]
    data = []
    for meter_node in meternode_mappings:
        data_obj = {
            "nodeId": meter_node.nodeId,
            "meterNumber": meter_node.meterNumber,
            "meterMaker": meter_node.meterMaker,
            "timestamp": meter_node.timestamp,
            "debugServerTime": meter_node.debugServerTime,
            "rfMeterType": meter_node.rfMeterType,
            "last_update_time": meter_node.last_update_time,
        }
        data.append(data_obj)
    json_data = {
        "draw": draw,
        "recordsFiltered": recordsTotal,
        "recordsTotal": recordsTotal,
        "data": data
    }
    return JsonResponse(json_data)


# Display duplicate meter node map table
def duplicate_meter_nodes(request):
    return render(request, 'data_pages/duplicate_meter_node.html')


#  Load duplicate meter node data
def load_duplicate_meter_nodes(request):
    dupl_meter_nodes = DuplicateMeterNode.objects.all()

    request_data = request.GET

    draw = int(request_data['draw'])
    length = int(request_data['length'])
    start = int(request_data['start'])

    # filter by meterNumber or nodeId or existing meter_node
    search_value = request_data['search[value]']
    if search_value:
        searchvalue = int(search_value) if search_value.isdecimal() else None
        if searchvalue is None:
            dupl_meter_nodes = dupl_meter_nodes.filter(Q(meterNumber__contains=search_value) | Q(existingMeterNumber__contains=search_value))
        else:
            dupl_meter_nodes = dupl_meter_nodes.filter(Q(nodeId__contains=search_value) | Q(meterNumber__contains=search_value) | Q(existingMeterNumber__contains=search_value))
    # filter by datetime
    from_time = request_data['from_time']
    till_time = request_data['till_time']
    if from_time and till_time:
        from_time = datetime.datetime.strptime(str(from_time), '%Y-%m-%d %H:%M:%S')
        till_time = datetime.datetime.strptime(str(till_time), '%Y-%m-%d %H:%M:%S')
        dupl_meter_nodes = dupl_meter_nodes.filter(debugServerTime__gte=from_time, debugServerTime__lte=till_time)

    sort_column_num = int(request_data['order[0][column]'])
    sort_column = str(request_data[f"columns[{sort_column_num}][name]"])
    sort_column_dir = str(request_data['order[0][dir]'])
    if sort_column_dir == "desc":
        dupl_meter_nodes = dupl_meter_nodes.order_by(f"-{sort_column}")
    else:
        dupl_meter_nodes = dupl_meter_nodes.order_by(sort_column)

    recordsTotal = len(dupl_meter_nodes)
    dupl_meter_nodes = dupl_meter_nodes[start:start + length]
    data = []
    for d_meter_node in dupl_meter_nodes:
        data_obj = {
            "nodeId": d_meter_node.nodeId,
            "meterNumber": d_meter_node.meterNumber,
            "existingMeterNumber": d_meter_node.existingMeterNumber,
            "timestamp": d_meter_node.timestamp,
            "debugServerTime": d_meter_node.debugServerTime,
            "last_update_time": d_meter_node.last_update_time,
        }
        data.append(data_obj)
    json_data = {
        "draw": draw,
        "recordsFiltered": recordsTotal,
        "recordsTotal": recordsTotal,
        "data": data
    }
    return JsonResponse(json_data)
