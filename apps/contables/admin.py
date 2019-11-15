# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import *
from import_export.admin import ImportExportModelAdmin

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

# Register your models here.

#Orden de Fabricacion y Planilla
class empleadoAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('nombres','id', 'apellidos', 'edad', 'sexo', 'direccion', 'telefono', 'contacto','dui', 'nit', 'afp', 'puesto', 'activo')
    list_filter = ('edad','sexo','puesto', 'activo')
    search_fields = ('id','nombres', 'apellidos', 'edad', 'sexo', 'direccion', 'telefono', 'contacto','dui', 'nit', 'afp', 'puesto',)


class puestoAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('nombre','id',  'salarioMensual')
    search_fields = ('id', 'nombre', 'salarioMensual')


class clienteAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('nombre', 'id','nit', 'telefono')
    search_fields = ('nombre', 'id','nit','telefono')

class ordenAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('cliente','fechaExpedicion', 'fechaRequerida', 'materal','catidadMP','costoUnitarioMP','totalMP','obrero','numHoras',
                    'costoHora','totalMOD','tasaCIF', 'importe')
    search_fields = ('fechaExpedicion', 'fechaRequerida', 'materal','catidadMP','costoUnitarioMP','totalMP','obrero','numHoras',
                     'costoHora','totalMOD','tasaCIF', 'importe')

class productoAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('ordenDeFabricacion', 'nuneroArticulos','costoUnitario')
    exclude =('inventarioInicialMp', 'compras', 'inventarioFinal', 'invIniPenP', 'invFinalPenP', 'invInicialProductTerminado', 'invFinalProductTerminado')
    search_fields = ('numProducto','nombre', 'ordenDeFabricacion', 'nuneroArticulos','costoUnitario')

admin.site.register(Empleado, empleadoAdmin)
admin.site.register(Puesto, puestoAdmin)
admin.site.register(ordenDeFabricacion, ordenAdmin)
admin.site.register(Cliente, clienteAdmin)
admin.site.register(producto, productoAdmin)


#cuentas

class TipoCuentaAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    ordering = ["codigo"]
    list_filter = ['codigo']
    search_fields = ["nombre"]

class RubroAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo')
    list_filter = ['tipo']
    search_fields = ["nombre"]


class CuentaMayorAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'rubro')
    list_filter = ['rubro']
    search_fields = ["nombre"]

class CuentaAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'acreedor', 'tipo', 'rubro', 'cuentaMayor', 'montoDebe', 'montoHaber', 'totalCuenta')
    exclude =('montoDebe','montoHaber','totalCuenta')
    list_filter = ['cuentaMayor']
    search_fields = ["nombre"]


admin.site.register(TipoCuenta, TipoCuentaAdmin)
admin.site.register(Rubro, RubroAdmin)
admin.site.register(CuentaMayor, CuentaMayorAdmin)
admin.site.register(Cuenta, CuentaAdmin)

#Transacciones
class TipoTransaccionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	display = ('nombre')

class TransaccionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	list_display = ('codigo', 'fecha', 'empleado', 'tipo', 'descripcion', 'montoDebe', 'montoHaber')

class MovimientoAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('cuenta', 'debe', 'cantidad', 'empleado', 'transaccion')



admin.site.register(TipoTransaccion, TipoTransaccionAdmin)
admin.site.register(Movimiento, MovimientoAdmin)
admin.site.register(Transaccion, TransaccionAdmin)
admin.site.register(Mes)


#Contabilidad de costo, kardex

class MovimientoInventarioAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display=('idAuxiliar', 'fecha','detalle','eCantidad','ePUnitario','eTotal','sCantidad','sPUnitario','sTotal','saldoCantidad','saldoPUnitario','saldoTotal')
    

admin.site.register(MovimientoInventario,MovimientoInventarioAdmin)
admin.site.register(CuentaBalanceGeneral)
admin.site.register(PoliticaEmpresa)

admin.site.site_header = 'Sitio Administrativo Contable'
