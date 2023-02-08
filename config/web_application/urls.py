from django.urls import path
from .views import *
urlpatterns = [
    path('', dashboard),
    path('dashboard', dashboard),

    path('dcus', dcus),
    path('load_dcus', load_dcus),

    path('dcu_node_mappings', dcu_node_mappings),
    path('load_dcu_node_mappings', load_dcu_node_mappings),

    path('meter_node_mappings', meter_node_mappings),
    path('load_meter_node_mappings', load_meter_node_mappings),

    path('duplicate_meter_nodes', duplicate_meter_nodes),
    path('load_duplicate_meter_nodes', load_duplicate_meter_nodes),
]
