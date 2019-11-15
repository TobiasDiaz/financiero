# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, time, timedelta, date
from django.core.urlresolvers import reverse
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Count

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

# Create your models here.

#Orden de Fabricacion y Planilla
class Puesto(models.Model):
   
    nombre = models.CharField(max_length=30, null=False)
    salarioMensual = models.FloatField(default=0.0, null=False)

    def get_salario_diario(self):
        return self.salarioMensual / 30

    def get_salario_real(self):
        return (self.get_salario_diario()*7)/5.5

    def get_salario_nominal(self):
        return self.get_salario_real()*7

    def get_vacaciones(self):
        return self.get_salario_diario()*15*1.3

    def get_prestaciones(self):
        return (self.get_salario_diario() * 15) * 0.1525

    def get_cotizaciones_y_vacaciones(self):    #El dato 0.1525 debe sacarse de la BD, y es el total de prestaciones
        return self.get_vacaciones() + self.get_prestaciones()

    def get_provision_semanal(self):
        return self.get_cotizaciones_y_vacaciones() / 52

    def get_cotizacion_semanal(self):
        return self.get_salario_nominal()*0.1525

    class Meta:
        verbose_name='Puesto'
        verbose_name_plural='Puestos'
    def __str__(self):
        return '%s' %(self.nombre)



# Create your models here.
class Empleado(models.Model):
    sexo_opt = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    )

    nombres = models.CharField(max_length=50, null=False)
    apellidos = models.CharField(max_length=50, null=False)
    edad = models.IntegerField(null=False)
    sexo = models.CharField(max_length=1, choices=sexo_opt, null=False)
    direccion = models.TextField(max_length=200, null=False)
    telefono = models.CharField(max_length=9, null=False)
    contacto = models.CharField(max_length=9, null=False)
    dui = models.CharField(max_length=10, null=False)
    nit = models.CharField(max_length=17, null=False)
    afp = models.CharField(max_length=12, null=False)
    eficiencia = models.FloatField(default=0.9)
    puesto = models.ForeignKey(Puesto, on_delete=models.CASCADE)
    activo = models.BooleanField()
    fecha_contratacion = models.DateField(default='2001-01-01')

    def get_dias_contratado(self):
        f1 = self.fecha_contratacion
        delta = date.today() - f1

        return delta.days

    def get_aguinaldo(self):
        dias = self.get_dias_contratado()
        salario_diario = self.puesto.get_salario_diario()

        if dias >= 0 and dias < 1080:           #Si ha trabajado hasta menos de 3 años
            # if datetime.today() >= date.today().replace(month=12, day=12):      #Si hoy
            return salario_diario*15
        elif dias >= 1080 and dias < 3600:      #Si ha trabajado desde 3 hasta 10 años
            return salario_diario*19
        elif dias >= 3600:                      #Si ha trabajado de 10 años en adelante
            return salario_diario*21

    def get_aguinaldo_semanal(self):
        return self.get_aguinaldo()/52

    def get_salario_semanal(self):
        sum = self.puesto.get_salario_nominal() + self.get_aguinaldo_semanal() + \
              self.puesto.get_provision_semanal() + self.puesto.get_cotizacion_semanal()

        return sum

    def get_factor_recargo(self):
        return self.get_salario_semanal() / self.puesto.get_salario_nominal()

    def get_factor_recargo_eficiencia(self):
        return self.get_factor_recargo() / self.eficiencia

    def get_salario_mensual(self):
        return self.get_salario_semanal() * 4

    def get_absolute_url(self):
        return reverse('empleado_detail', kwargs={"pk":self.pk})

    class Meta:
        verbose_name='Empleado'
        verbose_name_plural='Empleado'
    def __str__(self):
        return '%s' %(self.nombres+" "+self.apellidos)


class Cliente(models.Model):
    nombre = models.CharField(max_length=100, null=False)
    nit = models.CharField(max_length=17, null=False)
    telefono = models.CharField(max_length=9, null=False)

    class Meta:
        verbose_name='Cliente'
        verbose_name_plural='Clientes'
    def __str__(self):
        return '%s' %(self.nombre)

class ordenDeFabricacion(models.Model):
    
    cliente=models.ForeignKey(Cliente, default=1)
    fechaExpedicion=models.DateField()
    fechaRequerida=models.DateField()
    materal=models.CharField(max_length=100, null=False)
    catidadMP=models.FloatField()
    costoUnitarioMP=models.FloatField()
    obrero=models.ForeignKey(Empleado, null=False)
    numHoras=models.IntegerField()
    costoHora=models.FloatField()
    tasaCIF=models.FloatField()


    def totalMP(self):
        return self.catidadMP*self.costoUnitarioMP

    def totalMOD(self):
        return self.numHoras*self.costoHora

    def importe(self):
        return (self.catidadMP*self.costoUnitarioMP)*self.tasaCIF

    class Meta:
        verbose_name='Orden de Fabricacion'
        verbose_name_plural='Ordenes de Fabricacion'
    def __str__(self):
        return '%s' %(self.materal)

class producto(models.Model):
    nombre=models.CharField(max_length=50, null=False)
    ordenDeFabricacion=models.ForeignKey(ordenDeFabricacion, null=False)
    inventarioInicialMp=models.FloatField(default=0.0)
    compras=models.FloatField(default=0.0)
    inventarioFinal=models.FloatField(default=0.0)
    invIniPenP=models.FloatField(default=0.0)
    invFinalPenP=models.FloatField(default=0.0)
    invInicialProductTerminado=models.FloatField(default=0.0)
    invFinalProductTerminado=models.FloatField(default=0.0)
    nuneroArticulos=models.IntegerField()



    def MPDisp(self):
        return self.inventarioInicialMp+self.compras

    def MPUtilizada(self):
        return self.ordenDeFabricacion.totalMP()

    def costoArtTerminado(self):
        return self.ordenDeFabricacion.totalMP()+self.invIniPenP+self.ordenDeFabricacion.totalMOD()+self.ordenDeFabricacion.importe()-self.invFinalPenP

    def artTerDisp(self):
        return self.ordenDeFabricacion.totalMP()+self.invIniPenP+self.ordenDeFabricacion.totalMOD()+self.ordenDeFabricacion.importe()-self.invFinalPenP+self.invInicialProductTerminado

    def costoVendido(self):
        return self.ordenDeFabricacion.totalMP()+self.invIniPenP+self.ordenDeFabricacion.totalMOD()+self.ordenDeFabricacion.importe()-self.invFinalPenP+self.invInicialProductTerminado-self.invFinalProductTerminado

    def costoUnitario(self):
        return (self.ordenDeFabricacion.totalMP()+self.invIniPenP+self.ordenDeFabricacion.totalMOD()+self.ordenDeFabricacion.importe()-self.invFinalPenP+self.invInicialProductTerminado-self.invFinalProductTerminado)/self.nuneroArticulos


    class Meta:
        verbose_name='Producto'
        verbose_name_plural='Productos'
    def __str__(self):
        return '%s' %(self.nombre)


		
		

#Codigo Cuentas

class PoliticaEmpresa(models.Model):
    nombre = models.CharField(max_length=50, null=False, unique=True)
    cantidad = models.FloatField(default=0.0)
    class Meta:
        verbose_name='Politica de la Empresa'
        verbose_name_plural='Politicas de la Empresa'
    def __str__(self):
        return '%s' %(self.nombre)

class CuentaBalanceGeneral(models.Model):
    nombre = models.CharField(max_length=50, null=False, unique=True)
    totalCuenta = models.FloatField(default=0.0)
    class Meta:
        verbose_name='Cuenta Balance General'
        verbose_name_plural='Cuentas Balance General'
    def __str__(self):
        return '%s' %(self.nombre)

class TipoCuenta(models.Model):
    codigo=models.IntegerField(default=1, unique=True,
        validators=[MaxValueValidator(9), MinValueValidator(1)])
    nombre = models.CharField(max_length=50, null=False, unique=True)
    class Meta:
        verbose_name='Tipo de Cuenta'
        verbose_name_plural='Tipos de Cuenta'
    def __str__(self):
        return '%s' %(self.nombre)

class Rubro(models.Model):
    tipo=models.ForeignKey(TipoCuenta, null=False)
    nombre=models.CharField(max_length=50, null=False, unique=True)

    def codigo(self):
        id1 = Rubro.objects.filter(tipo=self.tipo, id__lt=self.id)
        conta = id1.count()+1
        cod = str(self.tipo.codigo)+str(conta)
        return int(cod)
    class Meta:
        verbose_name='Rubro'
        verbose_name_plural='Rubros'
    def __str__(self):
        return '%s' %(self.nombre)


class CuentaMayor(models.Model):
    rubro=models.ForeignKey(Rubro, null=False)
    nombre=models.CharField(max_length=50, null=False, unique=True)
    def codigo(self):
        id1 = Rubro.objects.filter(tipo=self.rubro.tipo, id__lt=self.rubro.id)
        conta1 = id1.count()+1
        id2 = CuentaMayor.objects.filter(rubro=self.rubro, id__lt=self.id)
        conta2 = id2.count()
        cod = str(self.rubro.tipo.codigo)+str(conta1)+str(conta2)
        return int(cod)
    class Meta:
        verbose_name='Cuenta Mayor'
        verbose_name_plural='Cuentas Mayor'
    def __str__(self):
        return '%s' %(self.nombre)


class Cuenta(models.Model):
    nombre=models.CharField(max_length=50,  null=False, unique=True)
    acreedor=models.BooleanField(default=True)
    cuentaMayor=models.ForeignKey(CuentaMayor,null=True)
    montoDebe = models.FloatField(default=0.0)
    montoHaber = models.FloatField(default=0.0)
    totalCuenta = models.FloatField(default=0.0)

    def rubro(self):
        ru = Rubro.objects.get(nombre=self.cuentaMayor.rubro)
        return '%s' %(ru.nombre)

    def tipo(self):
        ti = TipoCuenta.objects.get(nombre=self.cuentaMayor.rubro.tipo.nombre)
        return '%s' %(ti.nombre)

    def codigo(self):
        id1 = Rubro.objects.filter(tipo=self.cuentaMayor.rubro.tipo, id__lt=self.cuentaMayor.rubro.id)
        conta1 = id1.count()+1
        id2 = CuentaMayor.objects.filter(rubro=self.cuentaMayor.rubro, id__lt=self.cuentaMayor.id)
        conta2 = id2.count()
        id3 = Cuenta.objects.filter(cuentaMayor=self.cuentaMayor, id__lt=self.id)
        conta3 = id3.count()+1
        cod = str(self.cuentaMayor.rubro.tipo.codigo)+str(conta1)+str(conta2)+str(conta3)
        return int(cod)


    class Meta:
        verbose_name='Cuenta'
        verbose_name_plural='Cuentas'
    def __str__(self):
        return '%s' %(self.nombre)

#Transacciones

class TipoTransaccion(models.Model):
    nombre = models.CharField(max_length=49, null=False)

    class Meta:
        verbose_name='Tipo Transaccion'
        verbose_name_plural='Tipo Transacciones'
    def __str__(self):
        return '%s' %(self.nombre)

class Transaccion(models.Model):
    fecha = models.DateField(default=datetime.now, null=False)
    empleado = models.ForeignKey(Empleado, null=False)
    tipo = models.ForeignKey(TipoTransaccion, null=False)
    descripcion=models.TextField(max_length=100, null=True)

    def codigo(self):
        contarId = Transaccion.objects.filter(id__lt=self.id)
        conta = contarId.count()+1
        return '%s' %(conta)

    def montoDebe(self):
        mov = Movimiento.objects.filter(transaccion=self.id, debe=1)
        debe=0.0
        for mov1 in mov:
            debe += mov1.cantidad
        return '%s' %(debe)

    def montoHaber(self):
        mov = Movimiento.objects.filter(transaccion=self.id, debe=0)
        haber=0.0
        for mov2 in mov:
            haber += mov2.cantidad
        return '%s' %(haber)

    class Meta:
        verbose_name='Transaccion'
        verbose_name_plural='Transacciones'
    def __str__(self):
        return str(self.id)

class Mes(models.Model):
    correlativo=models.IntegerField(default=1, unique=True,
        validators=[MaxValueValidator(12), MinValueValidator(1)])
    nombre = models.CharField(max_length=49, null=False)

    class Meta:
        verbose_name='Mes'
        verbose_name_plural='Meses'
    def __str__(self):
        return '%s' %(self.nombre)





class Movimiento(models.Model):
    transaccion=models.ForeignKey(Transaccion, null=False)
    cuenta=models.ForeignKey(Cuenta, null=False)
    cantidad=models.FloatField(default=0.0, null=True)
    debe=models.BooleanField(default=True)

    def empleado(self):
        empleado = Transaccion.objects.get(id=self.transaccion.id)
        return '%s' %(empleado.empleado)

    def fecha(self):
        fe = Transaccion.objects.get(id=self.transaccion.id)
        return '%s' %(fe.fecha)


    class Meta:
        verbose_name='Movimiento'
        verbose_name_plural='Movimientos'
    def __str__(self):
        return '%.2f' %(self.cantidad)



#kardex

class MovimientoInventario(models.Model):
    fecha = models.DateTimeField(auto_now=True)
    detalle= models.CharField(max_length=100,  null=False)
    eCantidad=models.IntegerField(default=0)
    ePUnitario=models.FloatField(default=0.0)
    eTotal=models.FloatField(default=0.0)
    sCantidad=models.IntegerField(default=0)
    sPUnitario=models.FloatField(default=0.0)
    sTotal=models.FloatField(default=0.0)
    saldoCantidad=models.IntegerField(default=0)
    saldoPUnitario=models.FloatField(default=0.0)
    saldoTotal=models.FloatField(default=0.0)
    idAux= models.IntegerField(default=0)

    def idAuxiliar(self):
        aux = MovimientoInventario.objects.filter(fecha__lt=self.fecha)
        contar=aux.count()+1
        return contar

    class Meta:
        verbose_name='MovimientoInventario'
        verbose_name_plural='MovimientoInventarios'
    def __str__(self):
        return '%s' %(self.detalle)


