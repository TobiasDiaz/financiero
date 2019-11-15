from __future__ import unicode_literals
from __future__ import absolute_import

from django.conf.urls import url
from apps.contables.views import *
from django.contrib.auth.decorators import login_required


urlpatterns = [
   url(r'^libro_diario/',libro_diario, name="baseLibroDiario"),
   url(r'^libro_diario_guardar/',libro_diario_guardar, name="baseLibroDiarioGuardar"),
   url(r'^libro_mayor/',libro_mayor, name="baseLibroMayor"),
   url(r'^libro_mayor_guardar/',libro_mayor_guardar, name="baseLibroMayorGuardar"),
   url(r'^cantidad_cuentas/',cantidad_cuentas, name="cantidadCuenta"),
   url(r'^transaccion/(?P<cantidad>\d+)/$', transaccion, name='transaccion'),
   url(r'^estados_financieros/',estados_financieros, name="baseEstadosFinancieros"),
   url(r'^ajustes_financieros/',ajustes_financieros, name="baseAjustesFinancieros"),
   url(r'^balance_comprobacion/',balance_comprobacion, name="baseBalanceComprobacion"),
   url(r'^balance_comprobacion_guardar/',balance_comprobacion_guardar, name="baseBalanceComprobacion_guardar"),
   url(r'^estado_de_resultado/',estado_de_resultado,name='estadoDeResultado'),
   url(r'^estado_de_resultado_ingreso/',estado_de_resultado_ingreso,name='estadoDeResultado_ingreso'),
   url(r'^estado_de_resultado_egreso/',estado_de_resultado_egreso,name='estadoDeResultado_egreso'),
   url(r'^estado_de_resultado_total/',estado_de_resultado_total,name='estadoDeResultado_total'),
   url(r'^estado_de_capital/',estado_de_capital,name='estadoDeCapital'),
   url(r'^estado_de_capital_inversiones/',estado_de_capital_inversiones,name='estadoDeCapital_inversiones'),
   url(r'^estado_de_capital_desinversiones/',estado_de_capital_desinversiones,name='estadoDeCapital_desinversiones'),
   url(r'^estado_de_capital_total/',estado_de_capital_total,name='estadoDeCapital_total'),
   url(r'^balance_general/',balance_general,name='balanceGeneral'),
   url(r'^balance_general_activo/',balance_general_activo,name='balanceGeneral_activo'),
   url(r'^balance_general_pasivo/',balance_general_pasivo,name='balanceGeneral_pasivo'),
   url(r'^balance_general_total/',balance_general_total,name='balanceGeneral_total'),


   url(r'^contactenos/',contactenos, name="baseContactenos"),
   url(r'^servicios/',servicios, name="baseServicios"),
   url(r'^ayuda/$',ayuda, name="ayuda"),

   url(r'^ordenes_de_fabricacion/',orden_de_fabricacion, name="baseOrdenDeFabricacion"),
   url(r'^costeo/',costeo, name="baseCosteo"),

   
   url(r'^planillaPago/',listar_planilla,name='basePlanilla'),
   url(r'^inventarioMateriaPrima/',inventarioMateriaPrima,name='baseInventarioMateriaPrima'),
   url(r'^catalogoCuenta/',catalogoCuenta,name='baseCatalogoCuenta'),
   url(r'^detalle_empleado/(?P<id_empleado>\d+)/$',detalle_empleado, name='detalle_empleado'),
   url(r'^ordenes/$', login_required(ListaOrdenes.as_view()), name="ordenes"),

    ##Costeo 
    url(r'^produccion/$', login_required(ListaProductos.as_view()), name="produccion"),
    url(r'^agregar_producto/$', login_required(crearProducto.as_view()), name="agregar_producto"),




    #Inventario
    url(r'^entradaProducto/',entradaProducto, name="baseEntradaProducto"),
    url(r'^salidaProducto/',salidaProducto, name="baseSalidaProducto"),
    url(r'^guardarProducto/',guardar_Entrada, name="baseGuardarEntrada"),
    url(r'^sacarProducto/',guardar_Salida, name="baseGuardarSalida"),
]