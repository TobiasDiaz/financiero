# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.shortcuts import render,redirect
from django.views.generic import ListView
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.paginator import Paginator,InvalidPage,EmptyPage
from django.views.generic import TemplateView,DetailView, CreateView
from models import *
from forms import ProductoForm
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from django.db.models import Count, Sum
import calendar
import datetime

ciclo = PoliticaEmpresa.objects.get(nombre="CICLO ACTIVO")
grupo = User.objects.raw('SELECT * FROM `auth_user_groups` AS UG INNER JOIN `auth_group` AS G ON G.id=UG.group_id')


# Create your views here.
@login_required(login_url='login')
def index(request):    
    return render(request,'Inicio/index.html',{'ciclo':ciclo, 'grupo':grupo})

def vista_login(request):
    username = request.POST.get('username','')
    password = request.POST.get('password','')
    user = auth.authenticate(username=username,password=password)
    print(username)
    print(password)
    if user is not None and user.is_active:
        auth.login(request,user)
        return HttpResponseRedirect("/account/loggedin/")
    else:
        return HttpResponseRedirect("/account/invalid/")

@login_required(login_url='login')
def libro_diario_guardar(request):
    today=datetime.datetime.now()
    mes=Mes.objects.get(correlativo=today.month)
    #lday=calendar.monthrange(today.year-1, today.month-1)[1]
    lday=today.day
    year=today.year
    movimiento = Movimiento.objects.all()
    return render(request,'Transaccion/libro_diario_guardar.html',{'ciclo':ciclo, 'grupo':grupo, 'lday':lday, 'mes':mes, 'year':year,'movimiento':movimiento})

@login_required(login_url='login')
def libro_diario(request):
    today=datetime.datetime.now()
    mes=Mes.objects.get(correlativo=today.month)
    #lday=calendar.monthrange(today.year-1, today.month-1)[1]
    lday=today.day
    year=today.year
    movimiento = Movimiento.objects.filter(transaccion__fecha__month=today.month)
    transaccion = Transaccion.objects.filter(fecha__month=today.month)
    paginador = Paginator(transaccion, 3)
    try:
        page = int(request.GET.get("page",'1'))
    except:
        page = 1
    try:
        transaccion = paginador.page(page)
    except(EmptyPage, InvalidPage):
        transaccion = paginador.page(paginador.num_pages)
    return render(request,'Transaccion/libro_diario.html',{'ciclo':ciclo, 'today':today, 'grupo':grupo, 'lday':lday, 'mes':mes, 'year':year,'movimiento':movimiento, 'transaccion':transaccion})

@login_required(login_url='login')
def libro_mayor(request):
    today=datetime.datetime.now()
    mes=Mes.objects.get(correlativo=today.month)
    #lday=calendar.monthrange(today.year-1, today.month-1)[1]
    lday=today.day
    year=today.year
    movimiento = Movimiento.objects.filter(transaccion__fecha__month=today.month)
    cuenta = Cuenta.objects.exclude(totalCuenta=0.0)
    paginador = Paginator(cuenta, 4)
    try:
        page = int(request.GET.get("page",'1'))
    except:
        page = 1
    try:
        cuenta = paginador.page(page)
    except(EmptyPage, InvalidPage):
        cuenta = paginador.page(paginador.num_pages)
    return render(request,'Transaccion/libro_mayor.html',{'ciclo':ciclo, 'grupo':grupo, 'lday':lday, 'mes':mes, 'year':year,'movimiento':movimiento, 'cuenta':cuenta})

@login_required(login_url='login')
def libro_mayor_guardar(request):
    today=datetime.datetime.now()
    mes=Mes.objects.get(correlativo=today.month)
    #lday=calendar.monthrange(today.year-1, today.month-1)[1]
    lday=today.day
    year=today.year
    cuenta = Cuenta.objects.exclude(totalCuenta=0.0)
    return render(request,'Transaccion/libro_mayor_guardar.html',{'ciclo':ciclo, 'grupo':grupo, 'lday':lday, 'mes':mes, 'year':year, 'cuenta':cuenta})

@login_required(login_url='login')
def cantidad_cuentas(request):
    cuenta=Cuenta.objects.all()
    canti=cuenta.count()
    if request.method == "POST":
        cantidad = int(request.POST['numero'])
        return HttpResponseRedirect(reverse('contable:transaccion', args=(cantidad,)))
    return render(request,'Transaccion/cantidadCuentas.html', {'ciclo':ciclo, 'grupo':grupo, 'canti':canti})

@login_required(login_url='login')
def transaccion(request, cantidad):
    cant = int(cantidad)
    empleado = Empleado.objects.all()
    tipoT = TipoTransaccion.objects.all()
    cuenta = Cuenta.objects.all()
    canti=Cuenta.objects.all()[:cant]
    debe=0.0
    haber=0.0
    igual=0

    if request.method == "POST":
        tran=Transaccion()
        tran.empleado_id=int(request.POST['empleado'])
        tran.tipo_id=int(request.POST['tipo'])
        tran.descripcion=request.POST['descripcion']
        tran.save()

        

        for x in xrange(1,int(cant)+1):
            mov=Movimiento()
            mov.cuenta_id=int(request.POST[str("cuenta")+str(x)])
            mov.cantidad=float(request.POST[str("saldo")+str(x)])
            mov.debe=int(request.POST[str("tipo")+str(x)])
            mov.transaccion_id=tran.id
            mov.save()
            if mov.debe:
                debe+=mov.cantidad
            else:
                haber+=mov.cantidad
            pass

        cuen=Movimiento.objects.filter(transaccion_id=tran.id)
        for cx in cuen:
            for cy in cuen:
                if cx.cuenta == cy.cuenta:
                    igual +=1

        if tran.tipo.nombre == "Venta":
            cuentD = Cuenta.objects.get(nombre="IVA DEBITO FISCAL")
            movA= Movimiento.objects.get(cuenta__cuentaMayor__rubro__tipo__nombre="Activo", transaccion_id=tran.id)
            movD=Movimiento()
            movD.cuenta_id=cuentD.id
            movD.cantidad=(movA.cantidad)*0.13
            movD.debe=0
            movD.transaccion_id=tran.id
            movD.save()
            movA.cantidad+=movD.cantidad
            movA.save()

        if tran.tipo.nombre == "Devolucion sobre venta":
            cuentD = Cuenta.objects.get(nombre="IVA DEBITO FISCAL")
            movA= Movimiento.objects.get(cuenta__cuentaMayor__rubro__tipo__nombre="Activo", transaccion_id=tran.id)
            movD=Movimiento()
            movD.cuenta_id=cuentD.id
            movD.cantidad=(movA.cantidad)*0.13
            movD.debe=1
            movD.transaccion_id=tran.id
            movD.save()
            movA.cantidad+=movD.cantidad
            movA.save()

        if tran.tipo.nombre == "Compra":
            cuentD = Cuenta.objects.get(nombre="IVA CREDITO FISCAL")
            movA= Movimiento.objects.get(cuenta__cuentaMayor__rubro__tipo__nombre="Activo", transaccion_id=tran.id, debe=0)
            movD=Movimiento()
            movD.cuenta_id=cuentD.id
            movD.cantidad=(movA.cantidad)*0.13
            movD.debe=1
            movD.transaccion_id=tran.id
            movD.save()
            movA.cantidad+=movD.cantidad
            movA.save()

        if tran.tipo.nombre == "Devolucion sobre compra":
            cuentD = Cuenta.objects.get(nombre="IVA CREDITO FISCAL")
            movA= Movimiento.objects.get(cuenta__cuentaMayor__rubro__tipo__nombre="Activo", transaccion_id=tran.id, debe=0)
            movD=Movimiento()
            movD.cuenta_id=cuentD.id
            movD.cantidad=(movA.cantidad)*0.13
            movD.debe=1
            movD.transaccion_id=tran.id
            movD.save()
            movA.cantidad+=movD.cantidad
            movA.save()


        if debe == haber:
            if igual == ((cant*cant)-cant):
                return HttpResponseRedirect('/libro_diario/')
            else:
                mensaje = "No pueden usarse las misma cuentas"
                borrar = Transaccion.objects.filter(id=tran.id).delete()
                return render(request,'Transaccion/transaccion.html', {'ciclo':ciclo, 'grupo':grupo, 'cant':cant, 'empleado':empleado, 'tipoT':tipoT, 'canti':canti, 'cuenta':cuenta, 'mensaje':mensaje})
        else:
            mensaje = "Los montos debe y haber no son iguales"
            borrar = Transaccion.objects.filter(id=tran.id).delete()
            return render(request,'Transaccion/transaccion.html', {'ciclo':ciclo, 'grupo':grupo, 'cant':cant, 'empleado':empleado, 'tipoT':tipoT, 'canti':canti, 'cuenta':cuenta, 'mensaje':mensaje})

    return render(request,'Transaccion/transaccion.html', {'ciclo':ciclo, 'grupo':grupo, 'cant':cant, 'empleado':empleado, 'tipoT':tipoT, 'canti':canti, 'cuenta':cuenta})

@login_required(login_url='login')
def estados_financieros(request):
    return render(request, 'Informes/estados_financieros.html')

@login_required(login_url='login')
def balance_comprobacion(request):
    today=datetime.datetime.now()
    mes=Mes.objects.get(correlativo=today.month)
    #lday=calendar.monthrange(today.year-1, today.month-1)[1]
    lday=today.day
    year=today.year
    moviDebe = Movimiento.objects.raw('SELECT SUM(cantidad) AS Total, id, cuenta_id FROM contables_movimiento WHERE debe=1 GROUP BY cuenta_id')
    moviHaber = Movimiento.objects.raw('SELECT SUM(cantidad) AS Total, id, cuenta_id FROM contables_movimiento WHERE debe=0 GROUP BY cuenta_id')
    cuenta =Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre FROM contables_movimiento AS M INNER JOIN contables_cuenta AS C on M.cuenta_id=C.id INNER JOIN contables_cuentaMayor AS CM on C.cuentaMayor_id=CM.id INNER JOIN contables_rubro AS R on CM.rubro_id=R.id INNER JOIN contables_tipocuenta AS T on R.tipo_id=T.id GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    cuentaS=Cuenta.objects.all()
    for cuentaD in cuentaS:
        for mov in moviDebe:
            if cuentaD.id == mov.cuenta.id:
                cuentaD.montoDebe=mov.Total
                cuentaD.save()

    for cuentaH in cuentaS:
        for mov in moviHaber:
            if cuentaH.id == mov.cuenta.id:
                cuentaH.montoHaber=mov.Total
                cuentaH.save()

    for cuentaT in cuentaS:
        if cuentaT.acreedor:
            cuentaT.totalCuenta=cuentaT.montoHaber-cuentaT.montoDebe
            cuentaT.save()
        else:
            cuentaT.totalCuenta=cuentaT.montoDebe-cuentaT.montoHaber
            cuentaT.save()
    totalDebe=Cuenta.objects.raw('SELECT SUM(totalCuenta) AS MontoDebeTotal, id, acreedor FROM contables_cuenta WHERE acreedor=0')
    totalHaber=Cuenta.objects.raw('SELECT SUM(totalCuenta) AS MontoHaberTotal, id, acreedor FROM contables_cuenta WHERE acreedor=1')
    return render(request, 'EstadosFinancieros/balanceComprobacion.html',{'ciclo':ciclo, 'grupo':grupo, 'year':year, 'mes':mes, 'lday':lday, 'moviDebe':moviDebe, 'cuenta':cuenta, 'moviHaber':moviHaber, 'totalDebe':totalDebe, 'totalHaber':totalHaber})

@login_required(login_url='login')
def balance_comprobacion_guardar(request):
    today=datetime.datetime.now()
    mes=Mes.objects.get(correlativo=today.month)
    #lday=calendar.monthrange(today.year-1, today.month-1)[1]
    lday=today.day
    year=today.year
    moviDebe = Movimiento.objects.raw('SELECT SUM(cantidad) AS Total, id, cuenta_id FROM contables_movimiento WHERE debe=1 GROUP BY cuenta_id')
    moviHaber = Movimiento.objects.raw('SELECT SUM(cantidad) AS Total, id, cuenta_id FROM contables_movimiento WHERE debe=0 GROUP BY cuenta_id')
    cuenta =Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre FROM contables_movimiento AS M INNER JOIN contables_cuenta AS C on M.cuenta_id=C.id INNER JOIN contables_cuentaMayor AS CM on C.cuentaMayor_id=CM.id INNER JOIN contables_rubro AS R on CM.rubro_id=R.id INNER JOIN contables_tipocuenta AS T on R.tipo_id=T.id GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    cuentaS=Cuenta.objects.all()
    totalDebe=Cuenta.objects.raw('SELECT SUM(totalCuenta) AS MontoDebeTotal, id, acreedor FROM contables_cuenta WHERE acreedor=0')
    totalHaber=Cuenta.objects.raw('SELECT SUM(totalCuenta) AS MontoHaberTotal, id, acreedor FROM contables_cuenta WHERE acreedor=1')
    return render(request, 'EstadosFinancieros/balanceComprobacion_guardar.html',{'ciclo':ciclo, 'grupo':grupo, 'year':year, 'mes':mes, 'lday':lday, 'moviDebe':moviDebe, 'cuenta':cuenta, 'moviHaber':moviHaber, 'totalDebe':totalDebe, 'totalHaber':totalHaber})


@login_required(login_url='login')
def estado_de_resultado(request):
    today=datetime.datetime.now()
    mes=Mes.objects.get(correlativo=today.month)
    #lday=calendar.monthrange(today.year-1, today.month-1)[1]
    lday=today.day
    year=today.year
    cuentasA=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre, C.totalCuenta FROM contables_movimiento AS M INNER JOIN contables_cuenta AS C on M.cuenta_id=C.id INNER JOIN contables_cuentaMayor AS CM on C.cuentaMayor_id=CM.id INNER JOIN contables_rubro AS R on CM.rubro_id=R.id INNER JOIN contables_tipocuenta AS T on R.tipo_id=T.id AND T.nombre="RESULTADO ACREEDORA" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    cuentasD=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre, C.totalCuenta FROM contables_movimiento AS M INNER JOIN contables_cuenta AS C on M.cuenta_id=C.id INNER JOIN contables_cuentaMayor AS CM on C.cuentaMayor_id=CM.id INNER JOIN contables_rubro AS R on CM.rubro_id=R.id INNER JOIN contables_tipocuenta AS T on R.tipo_id=T.id AND T.nombre="RESULTADO DEUDORA" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    totalI=0.00
    totalE=0.00

    for ingreso in cuentasA:
        totalI += ingreso.cuenta.totalCuenta

    for egreso in cuentasD:
        totalE += egreso.cuenta.totalCuenta

    utilidad=CuentaBalanceGeneral.objects.get(nombre="UTILIDADES DEL PERIODO")
    utilidad.totalCuenta= (totalI-totalE)
    utilidad.save()

    return render(request, 'EstadosFinancieros/estadoResultado.html',{'ciclo':ciclo, 'grupo':grupo, 'lday':lday, 'mes':mes, 'year':year, 'cuentasA':cuentasA, 'totalI':totalI, 'cuentasD':cuentasD, 'totalE':totalE, 'utilidad':utilidad})

@login_required(login_url='login')
def estado_de_resultado_ingreso(request):
    today=datetime.datetime.now()
    mes=Mes.objects.get(correlativo=today.month)
    #lday=calendar.monthrange(today.year-1, today.month-1)[1]
    lday=today.day
    year=today.year
    cuentasA=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre, C.totalCuenta FROM contables_movimiento AS M INNER JOIN contables_cuenta AS C on M.cuenta_id=C.id INNER JOIN contables_cuentaMayor AS CM on C.cuentaMayor_id=CM.id INNER JOIN contables_rubro AS R on CM.rubro_id=R.id INNER JOIN contables_tipocuenta AS T on R.tipo_id=T.id AND T.nombre="RESULTADO ACREEDORA" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    cuentasD=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre, C.totalCuenta FROM contables_movimiento AS M INNER JOIN contables_cuenta AS C on M.cuenta_id=C.id INNER JOIN contables_cuentaMayor AS CM on C.cuentaMayor_id=CM.id INNER JOIN contables_rubro AS R on CM.rubro_id=R.id INNER JOIN contables_tipocuenta AS T on R.tipo_id=T.id AND T.nombre="RESULTADO DEUDORA" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    totalI=0.00
    totalE=0.00

    for ingreso in cuentasA:
        totalI += ingreso.cuenta.totalCuenta

    for egreso in cuentasD:
        totalE += egreso.cuenta.totalCuenta

    utilidad=CuentaBalanceGeneral.objects.get(nombre="UTILIDADES DEL PERIODO")
    utilidad.totalCuenta= (totalI-totalE)
    utilidad.save()

    return render(request, 'EstadosFinancieros/estadoResultado_ingreso.html',{'ciclo':ciclo, 'grupo':grupo, 'lday':lday, 'mes':mes, 'year':year, 'cuentasA':cuentasA, 'totalI':totalI, 'cuentasD':cuentasD, 'totalE':totalE, 'utilidad':utilidad})


@login_required(login_url='login')
def estado_de_resultado_egreso(request):
    today=datetime.datetime.now()
    mes=Mes.objects.get(correlativo=today.month)
    #lday=calendar.monthrange(today.year-1, today.month-1)[1]
    lday=today.day
    year=today.year
    cuentasA=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre, C.totalCuenta FROM contables_movimiento AS M INNER JOIN contables_cuenta AS C on M.cuenta_id=C.id INNER JOIN contables_cuentaMayor AS CM on C.cuentaMayor_id=CM.id INNER JOIN contables_rubro AS R on CM.rubro_id=R.id INNER JOIN contables_tipocuenta AS T on R.tipo_id=T.id AND T.nombre="RESULTADO ACREEDORA" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    cuentasD=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre, C.totalCuenta FROM contables_movimiento AS M INNER JOIN contables_cuenta AS C on M.cuenta_id=C.id INNER JOIN contables_cuentaMayor AS CM on C.cuentaMayor_id=CM.id INNER JOIN contables_rubro AS R on CM.rubro_id=R.id INNER JOIN contables_tipocuenta AS T on R.tipo_id=T.id AND T.nombre="RESULTADO DEUDORA" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    totalI=0.00
    totalE=0.00

    for ingreso in cuentasA:
        totalI += ingreso.cuenta.totalCuenta

    for egreso in cuentasD:
        totalE += egreso.cuenta.totalCuenta

    utilidad=CuentaBalanceGeneral.objects.get(nombre="UTILIDADES DEL PERIODO")
    utilidad.totalCuenta= (totalI-totalE)
    utilidad.save()

    return render(request, 'EstadosFinancieros/estadoResultado_egreso.html',{'ciclo':ciclo, 'grupo':grupo, 'lday':lday, 'mes':mes, 'year':year, 'cuentasA':cuentasA, 'totalI':totalI, 'cuentasD':cuentasD, 'totalE':totalE, 'utilidad':utilidad})

@login_required(login_url='login')
def estado_de_resultado_total(request):
    today=datetime.datetime.now()
    mes=Mes.objects.get(correlativo=today.month)
    #lday=calendar.monthrange(today.year-1, today.month-1)[1]
    lday=today.day
    year=today.year
    cuentasA=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre, C.totalCuenta FROM contables_movimiento AS M INNER JOIN contables_cuenta AS C on M.cuenta_id=C.id INNER JOIN contables_cuentaMayor AS CM on C.cuentaMayor_id=CM.id INNER JOIN contables_rubro AS R on CM.rubro_id=R.id INNER JOIN contables_tipocuenta AS T on R.tipo_id=T.id AND T.nombre="RESULTADO ACREEDORA" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    cuentasD=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre, C.totalCuenta FROM contables_movimiento AS M INNER JOIN contables_cuenta AS C on M.cuenta_id=C.id INNER JOIN contables_cuentaMayor AS CM on C.cuentaMayor_id=CM.id INNER JOIN contables_rubro AS R on CM.rubro_id=R.id INNER JOIN contables_tipocuenta AS T on R.tipo_id=T.id AND T.nombre="RESULTADO DEUDORA" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    totalI=0.00
    totalE=0.00

    for ingreso in cuentasA:
        totalI += ingreso.cuenta.totalCuenta

    for egreso in cuentasD:
        totalE += egreso.cuenta.totalCuenta

    utilidad=CuentaBalanceGeneral.objects.get(nombre="UTILIDADES DEL PERIODO")
    utilidad.totalCuenta= (totalI-totalE)
    utilidad.save()

    return render(request, 'EstadosFinancieros/estadoResultado_total.html',{'ciclo':ciclo, 'grupo':grupo, 'lday':lday, 'mes':mes, 'year':year, 'cuentasA':cuentasA, 'totalI':totalI, 'cuentasD':cuentasD, 'totalE':totalE, 'utilidad':utilidad})

@login_required(login_url='login')
def estado_de_capital(request):
    today=datetime.datetime.now()
    mes=Mes.objects.get(correlativo=today.month)
    #lday=calendar.monthrange(today.year-1, today.month-1)[1]
    lday=today.day
    year=today.year
    cuentasA=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre FROM `contables_movimiento` AS M INNER JOIN `contables_cuenta` AS C on M.cuenta_id=C.id and C.acreedor=1 INNER JOIN `contables_cuentaMayor` AS CM on C.cuentaMayor_id=CM.id INNER JOIN `contables_rubro` AS R on CM.rubro_id=R.id INNER JOIN `contables_tipocuenta` AS T on R.tipo_id=T.id AND T.nombre="PATRIMONIO" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    cuentasD=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre FROM `contables_movimiento` AS M INNER JOIN `contables_cuenta` AS C on M.cuenta_id=C.id and C.acreedor=0 INNER JOIN `contables_cuentaMayor` AS CM on C.cuentaMayor_id=CM.id INNER JOIN `contables_rubro` AS R on CM.rubro_id=R.id INNER JOIN `contables_tipocuenta` AS T on R.tipo_id=T.id AND T.nombre="PATRIMONIO" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    capitalP=PoliticaEmpresa.objects.get(nombre="POLITICA DE REINVERSION")
    utilidad=CuentaBalanceGeneral.objects.get(nombre="UTILIDADES DEL PERIODO")
    utilidadI=utilidad.totalCuenta*(capitalP.cantidad/100)
    totalI=utilidad.totalCuenta*(capitalP.cantidad/100)
    totalD=0.00

    for inversion in cuentasA:
        totalI += inversion.cuenta.totalCuenta

    for desinversion in cuentasD:
        totalD += desinversion.cuenta.totalCuenta

    capital=CuentaBalanceGeneral.objects.get(nombre="CAPITAL SOCIAL")
    capital.totalCuenta= (totalI-totalD)
    capital.save()

    return render(request, 'EstadosFinancieros/estadoCapital.html',{'ciclo':ciclo, 'grupo':grupo, 'lday':lday, 'mes':mes, 'year':year, 'cuentasA':cuentasA, 'totalI':totalI, 'cuentasD':cuentasD, 'totalD':totalD, 'utilidadI':utilidadI, 'capital':capital, 'capitalP':capitalP})

@login_required(login_url='login')
def estado_de_capital_inversiones(request):
    today=datetime.datetime.now()
    mes=Mes.objects.get(correlativo=today.month)
    #lday=calendar.monthrange(today.year-1, today.month-1)[1]
    lday=today.day
    year=today.year
    cuentasA=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre FROM `contables_movimiento` AS M INNER JOIN `contables_cuenta` AS C on M.cuenta_id=C.id and C.acreedor=1 INNER JOIN `contables_cuentaMayor` AS CM on C.cuentaMayor_id=CM.id INNER JOIN `contables_rubro` AS R on CM.rubro_id=R.id INNER JOIN `contables_tipocuenta` AS T on R.tipo_id=T.id AND T.nombre="PATRIMONIO" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    cuentasD=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre FROM `contables_movimiento` AS M INNER JOIN `contables_cuenta` AS C on M.cuenta_id=C.id and C.acreedor=0 INNER JOIN `contables_cuentaMayor` AS CM on C.cuentaMayor_id=CM.id INNER JOIN `contables_rubro` AS R on CM.rubro_id=R.id INNER JOIN `contables_tipocuenta` AS T on R.tipo_id=T.id AND T.nombre="PATRIMONIO" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    capitalP=PoliticaEmpresa.objects.get(nombre="POLITICA DE REINVERSION")
    utilidad=CuentaBalanceGeneral.objects.get(nombre="UTILIDADES DEL PERIODO")
    utilidadI=utilidad.totalCuenta*(capitalP.cantidad/100)
    totalI=utilidad.totalCuenta*(capitalP.cantidad/100)
    totalD=0.00

    for inversion in cuentasA:
        totalI += inversion.cuenta.totalCuenta

    for desinversion in cuentasD:
        totalD += desinversion.cuenta.totalCuenta

    capital=CuentaBalanceGeneral.objects.get(nombre="CAPITAL SOCIAL")
    capital.totalCuenta= (totalI-totalD)
    capital.save()

    return render(request, 'EstadosFinancieros/estadoCapital_inversiones.html',{'ciclo':ciclo, 'grupo':grupo, 'lday':lday, 'mes':mes, 'year':year, 'cuentasA':cuentasA, 'totalI':totalI, 'cuentasD':cuentasD, 'totalD':totalD, 'utilidadI':utilidadI, 'capital':capital, 'capitalP':capitalP})

@login_required(login_url='login')
def estado_de_capital_desinversiones(request):
    today=datetime.datetime.now()
    mes=Mes.objects.get(correlativo=today.month)
    #lday=calendar.monthrange(today.year-1, today.month-1)[1]
    lday=today.day
    year=today.year
    cuentasA=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre FROM `contables_movimiento` AS M INNER JOIN `contables_cuenta` AS C on M.cuenta_id=C.id and C.acreedor=1 INNER JOIN `contables_cuentaMayor` AS CM on C.cuentaMayor_id=CM.id INNER JOIN `contables_rubro` AS R on CM.rubro_id=R.id INNER JOIN `contables_tipocuenta` AS T on R.tipo_id=T.id AND T.nombre="PATRIMONIO" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    cuentasD=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre FROM `contables_movimiento` AS M INNER JOIN `contables_cuenta` AS C on M.cuenta_id=C.id and C.acreedor=0 INNER JOIN `contables_cuentaMayor` AS CM on C.cuentaMayor_id=CM.id INNER JOIN `contables_rubro` AS R on CM.rubro_id=R.id INNER JOIN `contables_tipocuenta` AS T on R.tipo_id=T.id AND T.nombre="PATRIMONIO" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    capitalP=PoliticaEmpresa.objects.get(nombre="POLITICA DE REINVERSION")
    utilidad=CuentaBalanceGeneral.objects.get(nombre="UTILIDADES DEL PERIODO")
    utilidadI=utilidad.totalCuenta*(capitalP.cantidad/100)
    totalI=utilidad.totalCuenta*(capitalP.cantidad/100)
    totalD=0.00

    for inversion in cuentasA:
        totalI += inversion.cuenta.totalCuenta

    for desinversion in cuentasD:
        totalD += desinversion.cuenta.totalCuenta

    capital=CuentaBalanceGeneral.objects.get(nombre="CAPITAL SOCIAL")
    capital.totalCuenta= (totalI-totalD)
    capital.save()

    return render(request, 'EstadosFinancieros/estadoCapital_desinversiones.html',{'ciclo':ciclo, 'grupo':grupo, 'lday':lday, 'mes':mes, 'year':year, 'cuentasA':cuentasA, 'totalI':totalI, 'cuentasD':cuentasD, 'totalD':totalD, 'utilidadI':utilidadI, 'capital':capital, 'capitalP':capitalP})

@login_required(login_url='login')
def estado_de_capital_total(request):
    today=datetime.datetime.now()
    mes=Mes.objects.get(correlativo=today.month)
    #lday=calendar.monthrange(today.year-1, today.month-1)[1]
    lday=today.day
    year=today.year
    cuentasA=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre FROM `contables_movimiento` AS M INNER JOIN `contables_cuenta` AS C on M.cuenta_id=C.id and C.acreedor=1 INNER JOIN `contables_cuentaMayor` AS CM on C.cuentaMayor_id=CM.id INNER JOIN `contables_rubro` AS R on CM.rubro_id=R.id INNER JOIN `contables_tipocuenta` AS T on R.tipo_id=T.id AND T.nombre="PATRIMONIO" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    cuentasD=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre FROM `contables_movimiento` AS M INNER JOIN `contables_cuenta` AS C on M.cuenta_id=C.id and C.acreedor=0 INNER JOIN `contables_cuentaMayor` AS CM on C.cuentaMayor_id=CM.id INNER JOIN `contables_rubro` AS R on CM.rubro_id=R.id INNER JOIN `contables_tipocuenta` AS T on R.tipo_id=T.id AND T.nombre="PATRIMONIO" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    capitalP=PoliticaEmpresa.objects.get(nombre="POLITICA DE REINVERSION")
    utilidad=CuentaBalanceGeneral.objects.get(nombre="UTILIDADES DEL PERIODO")
    utilidadI=utilidad.totalCuenta*(capitalP.cantidad/100)
    totalI=utilidad.totalCuenta*(capitalP.cantidad/100)
    totalD=0.00

    for inversion in cuentasA:
        totalI += inversion.cuenta.totalCuenta

    for desinversion in cuentasD:
        totalD += desinversion.cuenta.totalCuenta

    capital=CuentaBalanceGeneral.objects.get(nombre="CAPITAL SOCIAL")
    capital.totalCuenta= (totalI-totalD)
    capital.save()

    return render(request, 'EstadosFinancieros/estadoCapital_total.html',{'ciclo':ciclo, 'grupo':grupo, 'lday':lday, 'mes':mes, 'year':year, 'cuentasA':cuentasA, 'totalI':totalI, 'cuentasD':cuentasD, 'totalD':totalD, 'utilidadI':utilidadI, 'capital':capital, 'capitalP':capitalP})

@login_required(login_url='login')
def balance_general(request):
    today=datetime.datetime.now()
    mes=Mes.objects.get(correlativo=today.month)
    #lday=calendar.monthrange(today.year-1, today.month-1)[1]
    lday=today.day
    year=today.year
    cuentasA=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre FROM `contables_movimiento` AS M INNER JOIN `contables_cuenta` AS C on M.cuenta_id=C.id INNER JOIN `contables_cuentaMayor` AS CM on C.cuentaMayor_id=CM.id INNER JOIN `contables_rubro` AS R on CM.rubro_id=R.id INNER JOIN `contables_tipocuenta` AS T on R.tipo_id=T.id AND T.nombre="ACTIVO" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    cuentasP=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre FROM `contables_movimiento` AS M INNER JOIN `contables_cuenta` AS C on M.cuenta_id=C.id INNER JOIN `contables_cuentaMayor` AS CM on C.cuentaMayor_id=CM.id INNER JOIN `contables_rubro` AS R on CM.rubro_id=R.id INNER JOIN `contables_tipocuenta` AS T on R.tipo_id=T.id AND T.nombre="PASIVO" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    capitalP=PoliticaEmpresa.objects.get(nombre="POLITICA DE REINVERSION")
    por=100-capitalP.cantidad
    utilidad=CuentaBalanceGeneral.objects.get(nombre="UTILIDADES DEL PERIODO")
    utilidadR=utilidad.totalCuenta*(1-(capitalP.cantidad/100))
    ivaC=Cuenta.objects.get(nombre="IVA CREDITO FISCAL")
    ivaD=Cuenta.objects.get(nombre="IVA DEBITO FISCAL")
    if ivaC.totalCuenta >= ivaD.totalCuenta:
        ivaC.totalCuenta = ivaC.totalCuenta - ivaD.totalCuenta
        ivaC.save()
        ivaD.totalCuenta=0.0
        ivaD.save()
    else:
        ivaD.totalCuenta = ivaD.totalCuenta - ivaC.totalCuenta
        ivaD.save()
        ivaC.totalCuenta=0.0
        ivaC.save()
    totalA=0.00
    totalP=0.00

    for activo in cuentasA:
        if activo.cuenta.acreedor:
            totalA -= activo.cuenta.totalCuenta
        else:
            totalA += activo.cuenta.totalCuenta

    for pasivo in cuentasP:
        totalP += pasivo.cuenta.totalCuenta

    capital=CuentaBalanceGeneral.objects.get(nombre="CAPITAL SOCIAL")
    cuentaU=Cuenta.objects.get(nombre="Utilidad Retenida")
    totalK= utilidadR+capital.totalCuenta+cuentaU.totalCuenta

    totalPar= totalK + totalP

    return render(request, 'EstadosFinancieros/balanceGeneral.html',{'ciclo':ciclo, 'grupo':grupo, 'por':por, 'lday':lday, 'mes':mes, 'year':year, 'cuentasA':cuentasA, 'totalA':totalA, 'cuentasP':cuentasP, 'totalP':totalP, 'utilidadR':utilidadR, 'capital':capital, 'capitalP':capitalP, 'totalK':totalK, 'totalPar':totalPar})

@login_required(login_url='login')
def balance_general_activo(request):
    today=datetime.datetime.now()
    mes=Mes.objects.get(correlativo=today.month)
    #lday=calendar.monthrange(today.year-1, today.month-1)[1]
    lday=today.day
    year=today.year
    cuentasA=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre FROM `contables_movimiento` AS M INNER JOIN `contables_cuenta` AS C on M.cuenta_id=C.id INNER JOIN `contables_cuentaMayor` AS CM on C.cuentaMayor_id=CM.id INNER JOIN `contables_rubro` AS R on CM.rubro_id=R.id INNER JOIN `contables_tipocuenta` AS T on R.tipo_id=T.id AND T.nombre="ACTIVO" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    cuentasP=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre FROM `contables_movimiento` AS M INNER JOIN `contables_cuenta` AS C on M.cuenta_id=C.id INNER JOIN `contables_cuentaMayor` AS CM on C.cuentaMayor_id=CM.id INNER JOIN `contables_rubro` AS R on CM.rubro_id=R.id INNER JOIN `contables_tipocuenta` AS T on R.tipo_id=T.id AND T.nombre="PASIVO" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    capitalP=PoliticaEmpresa.objects.get(nombre="POLITICA DE REINVERSION")
    por=100-capitalP.cantidad
    utilidad=CuentaBalanceGeneral.objects.get(nombre="UTILIDADES DEL PERIODO")
    utilidadR=utilidad.totalCuenta*(1-(capitalP.cantidad/100))
    ivaC=Cuenta.objects.get(nombre="IVA CREDITO FISCAL")
    ivaD=Cuenta.objects.get(nombre="IVA DEBITO FISCAL")
    totalA=0.00
    totalP=0.00

    for activo in cuentasA:
        if activo.cuenta.acreedor:
            totalA -= activo.cuenta.totalCuenta
        else:
            totalA += activo.cuenta.totalCuenta

    for pasivo in cuentasP:
        totalP += pasivo.cuenta.totalCuenta

    capital=CuentaBalanceGeneral.objects.get(nombre="CAPITAL SOCIAL")
    cuentaU=Cuenta.objects.get(nombre="Utilidad Retenida")
    totalK= utilidadR+capital.totalCuenta+cuentaU.totalCuenta

    totalPar= totalK + totalP

    return render(request, 'EstadosFinancieros/balanceGeneral_activo.html',{'ciclo':ciclo, 'grupo':grupo, 'por':por, 'lday':lday, 'mes':mes, 'year':year, 'cuentasA':cuentasA, 'totalA':totalA, 'cuentasP':cuentasP, 'totalP':totalP, 'utilidadR':utilidadR, 'capital':capital, 'capitalP':capitalP, 'totalK':totalK, 'totalPar':totalPar})

@login_required(login_url='login')
def balance_general_pasivo(request):
    today=datetime.datetime.now()
    mes=Mes.objects.get(correlativo=today.month)
    #lday=calendar.monthrange(today.year-1, today.month-1)[1]
    lday=today.day
    year=today.year
    cuentasA=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre FROM `contables_movimiento` AS M INNER JOIN `contables_cuenta` AS C on M.cuenta_id=C.id INNER JOIN `contables_cuentaMayor` AS CM on C.cuentaMayor_id=CM.id INNER JOIN `contables_rubro` AS R on CM.rubro_id=R.id INNER JOIN `contables_tipocuenta` AS T on R.tipo_id=T.id AND T.nombre="ACTIVO" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    cuentasP=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre FROM `contables_movimiento` AS M INNER JOIN `contables_cuenta` AS C on M.cuenta_id=C.id INNER JOIN `contables_cuentaMayor` AS CM on C.cuentaMayor_id=CM.id INNER JOIN `contables_rubro` AS R on CM.rubro_id=R.id INNER JOIN `contables_tipocuenta` AS T on R.tipo_id=T.id AND T.nombre="PASIVO" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    capitalP=PoliticaEmpresa.objects.get(nombre="POLITICA DE REINVERSION")
    por=100-capitalP.cantidad
    utilidad=CuentaBalanceGeneral.objects.get(nombre="UTILIDADES DEL PERIODO")
    utilidadR=utilidad.totalCuenta*(1-(capitalP.cantidad/100))
    ivaC=Cuenta.objects.get(nombre="IVA CREDITO FISCAL")
    ivaD=Cuenta.objects.get(nombre="IVA DEBITO FISCAL")
    totalA=0.00
    totalP=0.00

    for activo in cuentasA:
        if activo.cuenta.acreedor:
            totalA -= activo.cuenta.totalCuenta
        else:
            totalA += activo.cuenta.totalCuenta

    for pasivo in cuentasP:
        totalP += pasivo.cuenta.totalCuenta

    capital=CuentaBalanceGeneral.objects.get(nombre="CAPITAL SOCIAL")
    cuentaU=Cuenta.objects.get(nombre="Utilidad Retenida")
    totalK= utilidadR+capital.totalCuenta+cuentaU.totalCuenta

    totalPar= totalK + totalP

    return render(request, 'EstadosFinancieros/balanceGeneral_pasivo.html',{'ciclo':ciclo, 'grupo':grupo, 'por':por, 'lday':lday, 'mes':mes, 'year':year, 'cuentasA':cuentasA, 'totalA':totalA, 'cuentasP':cuentasP, 'totalP':totalP, 'utilidadR':utilidadR, 'capital':capital, 'capitalP':capitalP, 'totalK':totalK, 'totalPar':totalPar})

@login_required(login_url='login')
def balance_general_total(request):
    today=datetime.datetime.now()
    mes=Mes.objects.get(correlativo=today.month)
    #lday=calendar.monthrange(today.year-1, today.month-1)[1]
    lday=today.day
    year=today.year
    cuentasA=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre FROM `contables_movimiento` AS M INNER JOIN `contables_cuenta` AS C on M.cuenta_id=C.id INNER JOIN `contables_cuentaMayor` AS CM on C.cuentaMayor_id=CM.id INNER JOIN `contables_rubro` AS R on CM.rubro_id=R.id INNER JOIN `contables_tipocuenta` AS T on R.tipo_id=T.id AND T.nombre="ACTIVO" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    cuentasP=Movimiento.objects.raw('SELECT COUNT(cuenta_id) AS repetida, M.id, C.nombre,T.nombre FROM `contables_movimiento` AS M INNER JOIN `contables_cuenta` AS C on M.cuenta_id=C.id INNER JOIN `contables_cuentaMayor` AS CM on C.cuentaMayor_id=CM.id INNER JOIN `contables_rubro` AS R on CM.rubro_id=R.id INNER JOIN `contables_tipocuenta` AS T on R.tipo_id=T.id AND T.nombre="PASIVO" GROUP BY cuenta_id ORDER BY T.codigo,R.id,CM.id')
    capitalP=PoliticaEmpresa.objects.get(nombre="POLITICA DE REINVERSION")
    por=100-capitalP.cantidad
    utilidad=CuentaBalanceGeneral.objects.get(nombre="UTILIDADES DEL PERIODO")
    utilidadR=utilidad.totalCuenta*(1-(capitalP.cantidad/100))
    ivaC=Cuenta.objects.get(nombre="IVA CREDITO FISCAL")
    ivaD=Cuenta.objects.get(nombre="IVA DEBITO FISCAL")
    totalA=0.00
    totalP=0.00

    for activo in cuentasA:
        if activo.cuenta.acreedor:
            totalA -= activo.cuenta.totalCuenta
        else:
            totalA += activo.cuenta.totalCuenta

    for pasivo in cuentasP:
        totalP += pasivo.cuenta.totalCuenta

    capital=CuentaBalanceGeneral.objects.get(nombre="CAPITAL SOCIAL")
    cuentaU=Cuenta.objects.get(nombre="Utilidad Retenida")
    totalK= utilidadR+capital.totalCuenta+cuentaU.totalCuenta

    totalPar= totalK + totalP

    return render(request, 'EstadosFinancieros/balanceGeneral_total.html',{'ciclo':ciclo, 'grupo':grupo, 'por':por, 'lday':lday, 'mes':mes, 'year':year, 'cuentasA':cuentasA, 'totalA':totalA, 'cuentasP':cuentasP, 'totalP':totalP, 'utilidadR':utilidadR, 'capital':capital, 'capitalP':capitalP, 'totalK':totalK, 'totalPar':totalPar})



@login_required(login_url='login')
def ajustes_financieros(request):
	return render(request,'Informes/ajustes_financieros.html')

@login_required(login_url='login')
def orden_de_fabricacion(request):
	return render(request,'Ordenes/orden_de_fabricacion.html',{'ciclo':ciclo, 'grupo':grupo})

@login_required(login_url='login')
def costeo(request):
	return render(request,'Costeo/costeo.html',{'ciclo':ciclo, 'grupo':grupo})

@login_required(login_url='login')
def inventarioMateriaPrima(request):
    movimiento = MovimientoInventario.objects.all().order_by('pk')
    return render(request,'Inventario/inventarioMateriaPrima.html',{'ciclo':ciclo, 'grupo':grupo, 'movimientos':movimiento})

@login_required(login_url='login')
def catalogoCuenta(request):
	tipoCuenta = TipoCuenta.objects.all().order_by('codigo')
	rubro = Rubro.objects.all()
	cuentaMayor = CuentaMayor.objects.all()
	cuenta = Cuenta.objects.all()
	return render(request,'Cuenta/catalogoCuentas.html',{'ciclo':ciclo, 'grupo':grupo, 'tipoCuenta':tipoCuenta, 'rubro':rubro, 'cuentaMayor':cuentaMayor, 'cuenta':cuenta})



def contactenos(request):
    return render(request,'Informacion/Contactenos.html',{'ciclo':ciclo, 'grupo':grupo})

def servicios(request):
    return render(request,'Informacion/Servicios.html',{'ciclo':ciclo, 'grupo':grupo})
def ayuda(request):
    return render(request,'Informacion/ayuda.html',{'ciclo':ciclo, 'grupo':grupo})


@login_required(login_url='login')
def listar_planilla(request):
	empleado = Empleado.objects.all()
	#template_name = 'Planilla/planilla.html'
	paginador=Paginator(empleado,4)   ##
	try:
		page=int(request.GET.get("page",'1'))
	except: 
		page=1
	try:
		empleado=paginador.page(page)
	except(EmptyPage,InvalidPage):
		empleado=paginador.page(paginador.num_pages)
	return render(request,'Planilla/planilla.html',{'ciclo':ciclo, 'grupo':grupo, 'empleados':empleado})

@login_required(login_url='login')
def detalle_empleado(request,id_empleado):
	empleado =Empleado.objects.get(id=id_empleado)
	return render(request,'Empleado/detalle_empleado.html',{'ciclo':ciclo, 'grupo':grupo, 'empleado':empleado} )
	


class ListaOrdenes(ListView):
    model = ordenDeFabricacion
    template_name = 'Ordenes/orden_de_fabricacion.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'Ordenes/orden_de_fabricacion.html', {
            'titulo':'Ordenes de Fabricación',
            'ciclo':ciclo, 
            'grupo':grupo, 
            'object_list': ordenDeFabricacion.objects.all()
        })
	



class ListaProductos(ListView):
    model = producto
    template_name = 'Costeo/produccion_ventas.html'

    def get(self, request, *args, **kwargs):
        # fecha = datetime.today().date()
        # fecha = fecha.replace(day=1)
        # productos = producto.objects.filter(ordenDeFabricacion__fechaExpedicion__year=fecha.year) \
        #     .filter(ordenDeFabricacion__fechaExpedicion__month=fecha.month)
        productos = producto.objects.all()

        totalMP = 0.0
        totalMOD = 0.0
        importe = 0.0
        costoArtTerminado = 0.0
        artTermDisp = 0.0
        costoVendido = 0.0

        for p in productos:
            totalMP += p.ordenDeFabricacion.totalMP()

        for p in productos:
            totalMOD += p.ordenDeFabricacion.totalMOD()

        for p in productos:
            importe += p.ordenDeFabricacion.importe()

        for p in productos:
            costoArtTerminado += p.costoArtTerminado()

        for p in productos:
            artTermDisp += p.artTerDisp()

        for p in productos:
            costoVendido += p.costoVendido()

        # if len(args) > 0:
        #     fecha.replace(month=args.index('mes'))
        #     fecha.replace(args.index('año'))

        return render(request, self.template_name, {
            'titulo': 'Producción y Ventas',
            'object_list': productos,
            'totalMP': totalMP,
            'totalMOD': totalMOD,
            'importe': importe,
            'grupo':grupo, 
            'costoArtTerminado': costoArtTerminado,
            'artTermDisp': artTermDisp,
            'ciclo':ciclo, 
            'costoVendido': costoVendido
        })


class crearProducto(CreateView):
    model = producto
    form_class = ProductoForm
    template_name = 'Costeo/agregar_producto.html'
    success_url = reverse_lazy('contable:produccion')




@login_required(login_url='login')
def entradaProducto(request):
    return render(request,'Inventario/entrada_Producto.html',{'ciclo':ciclo, 'grupo':grupo})

@login_required(login_url='login')
def salidaProducto(request):
    return render(request,'Inventario/salida_Producto.html',{'ciclo':ciclo, 'grupo':grupo})

@login_required(login_url='login')
def guardar_Entrada(request):
    if request.method == 'POST':
        
        gDetalle=request.POST['detalle']
        gCantidad=int(request.POST['cantidad'])
        gPUnitario=float(request.POST['pUnitario'])
        mensaje = " "
        #'/'.join(str(x) for x in (gFecha.month,gFecha.day,gFecha.year))
        gTotal=gCantidad*gPUnitario
        

        objeto=MovimientoInventario.objects.create(detalle=gDetalle,eCantidad=gCantidad,ePUnitario=gPUnitario,eTotal=gTotal,sCantidad=0,sPUnitario=0.0,sTotal=0.0,saldoCantidad=0,saldoPUnitario=0.0,saldoTotal=0.0)
        var= objeto.idAuxiliar()
        print var
        objeto.idAux=var
        objeto.save()

        id_ant=objeto.idAux ##guardo el id actual
        id_ant=id_ant-1   ## ya tenemos el id de la tupla anterior
        try:
            objeto_aux=MovimientoInventario.objects.get(idAux=id_ant) ##recupero objeto anterior
           #if objeto_aux.saldoCantidad < gCantidad:
                
            #    objeto.delete()
             #   mensaje= mensaje + "No hay Inventario Suficiente"
              #  return render(request,'Inventario/error.html',{'mensaje':mensaje})
            objeto_actual=MovimientoInventario.objects.get(idAux=objeto.idAux)##intentamos recuperar el objeto actual
            objeto_actual.saldoCantidad = objeto_actual.eCantidad + objeto_aux.saldoCantidad
            objeto_actual.saldoTotal = objeto_actual.eTotal + objeto_aux.saldoTotal
            objeto_actual.saldoPUnitario = objeto_actual.saldoTotal/objeto_actual.saldoCantidad
            objeto_actual.save()

        except ObjectDoesNotExist:

        
            objeto_aux=MovimientoInventario.objects.get(idAux=objeto.idAux)
            objeto_aux.saldoCantidad= gCantidad
            objeto_aux.saldoPUnitario = gPUnitario
            objeto_aux.saldoTotal = gTotal
            objeto_aux.save()


        print gDetalle
        print gCantidad
        print gPUnitario
        return redirect('contable:baseInventarioMateriaPrima')

@login_required(login_url='login')
def guardar_Salida(request):
    if request.method == 'POST':
        mensaje = " "
        gDetalle=request.POST['detalle']
        gCantidad=int(request.POST['cantidad'])
        j=0
        for i in MovimientoInventario.objects.all():
            j=j+1
        if j<=0:
            mensaje=mensaje + "Saldo de Inventario Inicial insuficiente"
            return render(request,'Inventario/error.html',{'mensaje':mensaje})
        objeto=MovimientoInventario.objects.create(detalle=gDetalle,eCantidad=0,ePUnitario=0,eTotal=0,sCantidad=gCantidad,sPUnitario=0.0,sTotal=0.0,saldoCantidad=0,saldoPUnitario=0.0,saldoTotal=0.0)
        var=  objeto.idAuxiliar()
        objeto.idAux = var
        objeto.save()

        id_ant=objeto.idAux
        id_ant=id_ant-1
    

        try:
            objeto_aux=MovimientoInventario.objects.get(idAux=id_ant)
            print objeto_aux.idAux
            if objeto_aux.saldoCantidad < gCantidad:
                
                objeto.delete()
                mensaje= mensaje + "No hay Inventario Suficiente"
                return render(request,'Inventario/error.html',{'mensaje':mensaje})
            objeto_actual=MovimientoInventario.objects.get(idAux=objeto.idAux)  ##recupero el actual

            objeto_actual.sPUnitario= objeto_aux.saldoPUnitario
            total = objeto_actual.sPUnitario * gCantidad
            objeto_actual.sTotal = total
            objeto_actual.saldoCantidad = objeto_aux.saldoCantidad - gCantidad
            objeto_actual.saldoPUnitario = objeto_aux.saldoPUnitario

            objeto_actual.saldoTotal = objeto_aux.saldoTotal - objeto_actual.sTotal
            if objeto_actual.saldoCantidad == 0:
                objeto_actual.saldoPUnitario =0
            objeto_actual.save()

        except ObjectDoesNotExist:
            objeto_actual=MovimientoInventario.objects.get(id=objeto.id)
          
        
        print gDetalle
        print gCantidad

        return redirect('contable:baseInventarioMateriaPrima')