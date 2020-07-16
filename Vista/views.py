from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template import Template,Context,loader
from bookflix.models import Usuario
from django.shortcuts import render,redirect
from django.contrib.auth import logout as do_logout, authenticate
from django.contrib.auth import login as do_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .forms import UserCreationFormExtends, UserEditForm, ProfileCreateForm,TarjetaCreacionForm,UsuarioCreacionForm
from django.contrib.auth.models import User
from .models import Perfil,Libro,Autor,Genero,Editorial,Precio,Tarjeta,Novedad,Calificacion,Capitulo,Favorito,Busqueda,Lectura,Comentario
import os
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import View
from django.core.exceptions import ValidationError
import datetime
import time

# Create your views here.

def holaMundo(request):
    return HttpResponse("Hola mundo")


def holaMundoTemplate(request):
    nombre = 'Agustin'
    diccionario = {'nombre': nombre}
    return render (request, "HolaMundo/holaMundo.html", diccionario)


def emptyPath(request):
    if estaLogueado(request):
        return redirect('/home/')
    return render(request,"emptyPath.html")

@login_required
def buscarLibro(request):
    return render(request,"busquedaLibro.html")

@login_required
def resultadosBusqueda(request):
    if request.GET["busqueda"] != "":
        busq=request.GET["busqueda"]
        text=busq.strip()
        #
        print(text)
        if request.GET["dist"]=="0":
            unPerfil=Perfil.objects.get(id=request.session.get("id"))
            busqq=Busqueda.objects.filter(quien=unPerfil)
            if(len(busqq)==0):
                    unaBusqueda = Busqueda(fecha=datetime.datetime.now(),quien=unPerfil,que=text)
                    unaBusqueda.save()
            else:
                if (busqq[len(busqq)-1].que == text):
                    var=busqq[len(busqq)-1]
                    var.delete()
                unaBusqueda = Busqueda(fecha=datetime.datetime.now(),quien=unPerfil,que=text)
                unaBusqueda.save()
        #
        if len(text)==0:
            text=request.GET["busqueda"]
            resultados=[]
            if(request.user.is_staff==0):
                perfil=request.session.get('id')
                perfil=Perfil.objects.get(id=int(perfil))
            return render(request,"resultadosBusqueda.html",{"libros":resultados,"que":text,"perfil":perfil})
        resultadosL=Libro.objects.filter(titulo__icontains=text)
        resultadosA=Libro.objects.filter(autor_id__nombre__icontains=text)
        librosSin2=[]
        librosCon2=[]
        #busca las coincidencias con los titulos, despues los autores y despues hace un set para sacar repetidos

        for l in resultadosL:
            venC=l.vencimiento.strftime("%Y/%m/%d")
            hoy=datetime.datetime.now().strftime("%Y/%m/%d")
            print('Vencimiento:',venC)
            print('Hoy:',hoy)
            print(venC<=hoy)
            if venC>hoy:
                autor=Autor(nombre=l.autor.nombre)
                libro=Libro(id=l.id,titulo=l.titulo,capitulado=l.capitulado,autor=autor,isbn=l.isbn)
                librosSin2.append(libro)
                autor2=Autor(nombre=l.autor.nombre)
                libro2=Libro(id=l.id,titulo=l.titulo,capitulado=l.capitulado,autor=autor2,isbn=l.isbn)
                librosCon2.append(libro2)


        for l in resultadosA:
            venC=l.vencimiento.strftime("%Y/%m/%d")
            hoy=datetime.datetime.now().strftime("%Y/%m/%d")
            print('Vencimiento:',venC)
            print('Hoy:',hoy)
            print(venC<=hoy)
            if venC>hoy:
                autor=Autor(nombre=l.autor.nombre)
                libro=Libro(id=l.id,titulo=l.titulo,capitulado=l.capitulado,autor=autor,isbn=l.isbn)
                librosSin2.append(libro)
                autor2=Autor(nombre=l.autor.nombre)
                libro2=Libro(id=l.id,titulo=l.titulo,capitulado=l.capitulado,autor=autor2,isbn=l.isbn)
                librosCon2.append(libro2)

        librosCon=list(set(librosCon2))
        librosSin=list(set(librosSin2))

        for lc in librosCon:
            lc.titulo=lc.titulo.replace(" ","_")
            lc.autor.nombre=lc.autor.nombre.replace(" ","_")

        dicci = {}
        dicci = {'que': text,'librosC':librosCon[0:6],'librosS':librosSin[0:6]}
        if(request.user.is_staff==0):
            perfil=request.session.get('id')
            perfil=Perfil.objects.get(id=int(perfil))
            dicci["perfil"]=perfil


    else:
        text=request.GET["busqueda"]
        resultados=[]
        dicci={}
        dicci={'que':text,'librosC':resultados,'librosS':resultados}
        if(request.user.is_staff==0):
            perfil=request.session.get('id')
            perfil=Perfil.objects.get(id=int(perfil))
            dicci["perfil"]=perfil
    return render(request,"resultadosBusqueda.html",dicci)
#USUARIOS
def registrame(request):
    if estaLogueado(request):
        return redirect('/')
    if request.method=="GET":
        vuelta=chequearCampos(request)
        error=vuelta[1]
        if (vuelta[0]):
            dnis=Usuario.objects.filter(dni=request.GET["dni"])
            if len(dnis) == 0:
                user=User()
                user.first_name=request.GET["name"].strip()
                user.last_name=request.GET["apellido"].strip()
                usernameA=request.GET["username"].strip()
                usernameA=str(usernameA).lower().replace(" ","")
                user.username=usernameA
                user.password=request.GET["password"].strip()
                user.email=request.GET["email"].strip()
                usuario=Usuario()
                usuario.user=user
                usuario.dni=request.GET["dni"]
                usuario.nacimiento=request.GET["nacimiento"]
                t=Tarjeta()
                num=(request.GET["numero"])
                t.num=str(num)
                t.cod=request.GET["cod"]
                t.nom=request.GET["nomT"].strip()
                t.venc=request.GET["fechaV"]
                usuario.tarjeta=t
                usuario.tipo=Precio.objects.get(tipo='Comun')
                perf=Perfil(usuario=usuario,nom=user.first_name,fecha=datetime.datetime.now())
                user.save()
                if validarTarjeta(t):
                    t.save()
                usuario.save()
                perf.foto="FotoPerfil1"
                perf.save()
                if user is not None:
                    do_login(request, user)
                    if(request.user.is_staff==0):
                        request.session["id"]=0
                        return redirect('/elegirPerfil/')
                    else:
                        request.session["id"]=1
                        return redirect('/home/')
            error=6
        campos={"error":error,"userN":request.GET["username"],"contra":request.GET["password"],"email":request.GET["email"],
                "nombre":request.GET["name"],"ape":request.GET["apellido"],"dni":request.GET["dni"],
                "birth":request.GET["nacimiento"],"numT":request.GET["numero"],"cod":request.GET["cod"],
                "nomT":request.GET["nomT"],"fechaV":request.GET["fechaV"]}
        return render(request, "registrarse.html",campos)
    print("VOY BIEN")
    return render(request, "registrarse.html",{"error":0})
#cod 1= username
#cod 2= password
#cod 3= email
#cod 4= nombre
#cod 5= apellido
#cod 6= dni
#cod 7= fecha de nacimiento
#cod 8= numero tarjeta
#cod 9= codigo tarjeta
#cod 10= titular tarjeta
#cod 11= vencimiento tarjeta

def validarTarjeta(tarjeta):
    return True

def chequearUser(request):
    dev=[False,0]
    nombre=request.GET["name"].strip()
    apellido=request.GET["apellido"].strip()
    contra=request.GET["password"]
    username=request.GET["username"].strip()
    email=request.GET["email"].strip()
    if (nombre!=""):
        if (apellido!=""):
            if(username!=""):
                if(email!=""):
                    if(contra!=""):
                        print("NINGUNO ERA VACIO")
                        if(len(contra)>=8):
                            if (len(User.objects.filter(username=username))==0):
                                if (len(User.objects.filter(email=email))==0):
                                    dev=[True,0]
                                else:
                                    print("Email repetido")
                                    dev[1]=3
                            else:
                                print("Username Repetido")
                                dev[1]=1
                        else:
                            print("contraseña corta")
                            dev[1]=2
                    else:
                        print("Contraseña en blanco")
                        dev[1]=22
                else:
                    print("email en blanco")
                    dev[1]=22
            else:
                print("username en blanco")
                dev[1]=22
        else:
            print("apellido en blanco")
            dev[1]=22
    else:
        print("nombre en blanco")
        dev[1]=22
    return dev

def chequearCampos(request):
    dev=[False,0]
    dni=request.GET["dni"]
    nac=request.GET["nacimiento"]
    numtar= request.GET["numero"]
    if numtar != "":
        numT=int(numtar)
    else:
        numT=""
    cod=request.GET["cod"]
    nomT=request.GET["nomT"].strip()
    fechaV=request.GET["fechaV"]
    if (dni!=""):
        if (nac!=""):
            año=int(nac[0:4])
            hoy=int(datetime.datetime.now().strftime("%Y"))
            dif=hoy-año
            if(dif>=18):
                if(numT!=""):
                    if ((numT>4000000000000000)&(numT<4999999999999999)):
                        if(cod!=""):
                            if((cod>'111')&(cod<'9999')):
                                if(nomT!=""):
                                    if(fechaV!=""):
                                        print("-------------------------------------------------")
                                        print(fechaV)
                                        print(datetime.datetime.now().strftime("%Y-%m-%d"))
                                        print("-------------------------------------------------")
                                        if(fechaV>datetime.datetime.now().strftime("%Y-%m-%d")):
                                            print("TODO BIEN")
                                            res=chequearUser(request)
                                            if res[0]:
                                                print("USER TAMBIEN TODO JOYA")
                                                dev=[True,0]
                                            else:
                                                dev=res
                                        else:
                                            print("fecha anterior a hoy")
                                            dev[1]=11
                                    else:
                                            print("fecha vacia")
                                            dev[1]=22
                                else:
                                            print("nombre vacio")
                                            dev[1]=22
                            else:
                                            print("codigo invalido")
                                            dev[1]=9
                        else:
                                            print("cod vacio")
                                            dev[1]=22
                    else:
                                        print("numero invalido")
                                        dev[1]=8
                else:
                                        print("numero vacio")
                                        dev[1]=22
            else:
                                        print("menor de edad")
                                        dev[1]=7
        else:
                                        print("fecha de nacimiento en blanco")
                                        dev[1]=22
    else:
                                        print("dni en blanco")
                                        dev[1]=22
    return dev

def signIn(request):
    if estaLogueado(request):
        return redirect('/')
    return render(request,"registrarse.html",{"error":0})

def login(request):
    if estaLogueado(request):
        return redirect('/home/')
    if request.method == 'POST':
        if ((request.POST["username"]=="")|(request.POST["password"]=="")):
            return render(request, "login.html", {'cod':1})
        else:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request,username=username, password=password)
            if user is None:
                hay = User.objects.filter(username=username,password=password)
                if len(hay)!=0:
                    user=User.objects.get(username=username,password=password)
            if user is not None:
                print("entre al login")
                do_login(request, user)
                if(request.user.is_staff==0):
                    request.session["id"]=0
                    return redirect('/elegirPerfil/')
                else:
                    request.session["id"]=1
                    return redirect('/home/')
        return render(request, "login.html", {'cod': 2})
    return render(request,"login.html",{"cod":0})
#cod=0: No hubo intento
#cod=1: Intento pero algun dato vacio
#cod=2: Intento pero algun dato equivocado

@login_required
def elegirPerfil(request):
    usu=Usuario.objects.get(user=request.user)
    perfiles=Perfil.objects.filter(usuario=usu)
    print(perfiles)
    print(perfiles[0].foto)
    if request.session["id"]==0:
        nuevo=True
        return render (request,'selectPerfil.html',{"perfiles":perfiles,"nuevo":nuevo})
    else:
        nuevo=False
        perfil=request.session.get('id')
        perfil=Perfil.objects.get(id=int(perfil))
        return render (request,'selectPerfil.html',{"perfiles":perfiles,"nuevo":nuevo,"perfil":perfil})

@login_required
def setPerfil(request):
    idPerfil=int(request.POST["idPerfil"])
    perfil=Perfil.objects.get(id=idPerfil)
    request.session['id']=perfil.id
    print(request.session)
    return redirect('/home/')


@login_required
def logout(request):
    do_logout(request)
    return redirect('/')


def queFoto(perfiles):
    if(len(perfiles)==1):
        return "FotoPerfil2"
    else:
        if len(perfiles)==2:
            return "FotoPerfil3"
        else:
            return "FotoPerfil4"

@login_required
def register_profile(request):
    usuario=Usuario.objects.get(user_id=request.user.id)
    cuantos=Perfil.objects.filter(usuario__id=usuario.id)
    if (usuario.tipo_id == 1):
        var=len(cuantos)<2
    else:
        var=len(cuantos)<4
    if request.method == "POST":
        if var:
            profile=Perfil()
            profile.nom = request.POST["nombre"]
            profile.usuario=Usuario.objects.get(user_id=request.user.id)
            profile.fecha=datetime.datetime.now()
            profile.foto=queFoto(cuantos)
            print("USE LA FOTO ",profile.foto)
            profile.save()
            return redirect('/miperfil/nuevoPerfil/')
    dicci={'perfiles':cuantos,'no':var}
    if(request.user.is_staff==0):
            perfil=request.session.get('id')
            perfil=Perfil.objects.get(id=int(perfil))
            dicci["perfil"]=perfil
    return render(request, "register_profile.html", dicci)

@login_required
def miperfil(request):
    usuario=Usuario.objects.get(user_id=request.user.id)
    if request.method == "POST":
        print(" A CHEQUEAR CAMPOS ")
        if (chequearCampos2(request)):
            tarjeta = Tarjeta.objects.get(id=usuario.tarjeta_id)
            user= User.objects.get(id=usuario.user_id)
            usuario.dni = request.POST["dni"]
            if request.POST["nacimiento"]!="":
                nac=request.POST["nacimiento"]
                año=int(nac[0:4])
                hoy=int(datetime.datetime.now().strftime("%Y"))
                dif=hoy-año
                if(dif>=18):
                    usuario.nacimiento = request.POST["nacimiento"]
                else:
                    dicci={"usu":usuario,"error":"La fecha de nacimiento ingresada corresponde a un menor de edad"}
                    if(request.user.is_staff==0):
                        perfil=request.session.get('id')
                        perfil=Perfil.objects.get(id=int(perfil))
                        dicci["perfil"]=perfil
                    return render(request,'miperfil.html',dicci)
            tarjeta.num = str(request.POST["numero"])
            tarjeta.cod = request.POST["cod"]
            tarjeta.nom = request.POST["nomT"]
            if request.POST["fechaV"]!="":
                fechaV=request.POST["fechaV"]
                if(fechaV>datetime.datetime.now().strftime("%Y-%m-%d")):
                    tarjeta.venc = request.POST["fechaV"]
                else:
                    dicci={"usu":usuario,"error":"La tarjeta esta vencida"}
                    if(request.user.is_staff==0):
                        perfil=request.session.get('id')
                        perfil=Perfil.objects.get(id=int(perfil))
                        dicci["perfil"]=perfil
                    return render(request,'miperfil.html',dicci)
            user.first_name = request.POST["nombre"]
            user.last_name = request.POST["apellido"]
            if chequearMail(request):
                user.email = request.POST["email"]
            else:
                dicci={"usu":usuario,"error":"Email ya existente en el sistema"}
                if(request.user.is_staff==0):
                    perfil=request.session.get('id')
                    perfil=Perfil.objects.get(id=int(perfil))
                    dicci["perfil"]=perfil
                return render(request,'miperfil.html',dicci)
            user.save()
            tarjeta.save()
            usuario.save()
            dicci={"usu":usuario,"error":"Datos modificados exitosamente"}
            if(request.user.is_staff==0):
                perfil=request.session.get('id')
                perfil=Perfil.objects.get(id=int(perfil))
                dicci["perfil"]=perfil
            return render(request,'miperfil.html',dicci)
        else:
            dicci={"usu":usuario,"error":"Los datos ingresados no son validos, por favor reviselos y vuelva a intentarlo"}
            if(request.user.is_staff==0):
                        perfil=request.session.get('id')
                        perfil=Perfil.objects.get(id=int(perfil))
                        dicci["perfil"]=perfil
            return render(request,'miperfil.html',dicci)
    dicci={"usu":usuario,}
    if(request.user.is_staff==0):
        perfil=request.session.get('id')
        perfil=Perfil.objects.get(id=int(perfil))
        dicci["perfil"]=perfil
    return render(request,'miperfil.html',dicci)

def chequearMail(request):
    aux1=User.objects.filter(email=request.POST["email"])
    if (len(aux1)==0):
        print("True: el mail no estaba en el sistema")
        return(True)
    else:
        if (request.user.email==request.POST["email"]):
            print("True: el mail es el mismo que ya estaba")
            return True
        else:
            print("False: el mail es de otro usuario")
            return False

def chequearCampos2(request):
    print("EN CHEQUEAR CAMPOS2")
    dni=request.POST["dni"]
    numT=str(request.POST["numero"])
    cod=request.POST["cod"]
    nomT=request.POST["nomT"]
    if (dni!=""):
        if(numT!=""):
            if ((numT>"4000000000000000")&(numT<"4999999999999999")):
                if((cod>'111')&(cod<'9999')):
                    if(nomT!=""):
                        return True
                    else:
                                print("nombre vacio")
                else:
                                print("codigo invalido")
            else:
                                print("numero invalido")
        else:
                                print("numero vacio")
    return False

def estaLogueado(request):
    resul=Usuario.objects.filter(user_id__username__icontains=request.user)
    aux= len(resul)==1
    print (aux)
    return aux

def obtenerNovedades():
    todasNovedades2 = Novedad.objects.all()
    todasNovedades=[]
    for i in range(len(todasNovedades2)-1,-1,-1):
        print(i)
        todasNovedades.append(todasNovedades2[i])
    print('--------------------------------')
    print(todasNovedades2)
    print(todasNovedades)
    print('--------------------------------')
    for each in todasNovedades:
        string= each.descripcion
        prev=''
        cont=0
        for i in range(0,len(string)):
            if cont<5:
                prev= prev + string[i]
                if string[i]==' ':
                    cont= cont + 1
        prev= prev + '...'
        each.descripcion=prev
    return todasNovedades

@login_required
def home(request):
    if request.session.get("id")==0:
        return redirect('/elegirPerfil/')
    todasNovedades = obtenerNovedades()
    libros = Libro.objects.all()
    librosSin=[]
    librosCon=[]
    for l in libros:
        venC=l.vencimiento.strftime("%Y/%m/%d")
        hoy=datetime.datetime.now().strftime("%Y/%m/%d")
        print('Vencimiento:',venC)
        print('Hoy:',hoy)
        print(venC<=hoy)
        if venC>=hoy:
            autor=Autor(nombre=l.autor.nombre)
            libro=Libro(id=l.id,titulo=l.titulo,capitulado=l.capitulado,autor=autor,isbn=l.isbn)
            librosSin.append(libro)
            autor2=Autor(nombre=l.autor.nombre)
            libro2=Libro(id=l.id,titulo=l.titulo,capitulado=l.capitulado,autor=autor2,isbn=l.isbn)
            librosCon.append(libro2)

    for lc in librosCon:
        lc.titulo=lc.titulo.replace(" ","_")
        lc.autor.nombre=lc.autor.nombre.replace(" ","_")

    print("---------------------------")
    print("LIBROS COMUNES:")
    print(librosSin)
    print("LIBROS CON GUION:")
    print(librosCon)
    print("---------------------------")
    dicci = {}
    if(request.user.is_staff==0):
        perfil=request.session.get('id')
        perfil=Perfil.objects.get(id=int(perfil))
        dicci = {'todos': todasNovedades,'librosC':librosCon[-6:],'librosS':librosSin[-6:],'perfil':perfil}
    else:
        dicci = {'todos': todasNovedades,'librosC':librosCon[-6:],'librosS':librosSin[-6:]}
    return render(request, "home.html", dicci)
    #return render(request, "PRUEBA.html", dicci)

def PRUEBA(request):
    todas=['papa','hijo','mama','hermano','stepsis']
    dicci = {'todas': todas}
    return render(request,'PRUEBA.HTML',dicci)

@login_required
def mostrarInfoLibro(request):
    if request.method=='GET':
        elLibro=Libro.objects.get(isbn=request.GET['isbn'])
        portada=elLibro.titulo.replace(" ","_") + "-" +elLibro.autor.nombre.replace(" ","_")
        calificaciones2=Calificacion.objects.filter(libro_id=elLibro.id)
        calificaciones=[]
        for i in range(len(calificaciones2)-1,-1,-1):
            print(i)
            calificaciones.append(calificaciones2[i])
        valor=0
        califico=False
        miCali=0
        print(calificaciones)
        usu=Perfil.objects.get(id=request.session.get("id"))
        for each in calificaciones:
            if (each.autor == usu):
                califico=True
                miCali=each.cuanto
            valor= valor + each.cuanto
        if len(calificaciones)!=0:
            calificacionF=valor/ len(calificaciones)
            calificacionF= int(calificacionF)
            calificado=True
        else:
            calificado=False
            calificacionF=-1


        comentarios2=Comentario.objects.filter(libro_id=elLibro.id)
        comentarios=[]
        for i in range(len(comentarios2)-1,-1,-1):
            print(i)
            comentarios.append(comentarios2[i])

        print(elLibro)
        print(comentarios)
        if len(comentarios)==0:
            comentado=False
        else:
            comentado=True

        if request.user.is_staff == 0:
            usu=Perfil.objects.get(id=request.session.get("id"))
            favoritos=Favorito.objects.filter(user=usu,libro_id=elLibro.id)
            if len(favoritos)==0:
                fav=False
            else:
                fav=True
        else:
            fav=False
        print('ENTRE HASTA ACA')
        unPerfil=Perfil.objects.get(id=request.session.get("id"))
        leyo= Lectura.objects.filter(isbn=elLibro.isbn,usuario=unPerfil)
        leyo= len(leyo)>0
        if elLibro.capitulado:
            hoy=datetime.datetime.now().strftime("%Y/%m/%d")
            capitulos=Capitulo.objects.filter(libro_id=elLibro.id)
            new=(len(capitulos)==0)
            vencimientos=[]
            if not(new):
                for each in capitulos:
                    print('DATOS ORIGINALES: '+ each.vencimiento.strftime("%Y/%m/%d") + ' ' + str(each.numero))
                    boola= each.vencimiento.strftime("%Y/%m/%d") >= hoy
                    aux=Libro(isbn=each.numero,capitulado=boola)
                    print('DATOS A APPEND: '+ str(aux.capitulado) + ' ' + str(aux.isbn))
                    vencimientos.append(aux)
                    impTodo(vencimientos)
            dicci={"libro":elLibro,"portada":portada,"calificacion":calificacionF,"pdf":vencimientos,"fav":fav,"hoy":hoy,"new":new,"comentarios":comentarios,"comentado":comentado,"calificaciones":calificaciones,"calificado":calificado,"califico":califico,"miCali":miCali,"leyo":leyo}
            if(request.user.is_staff==0):
                perfil=request.session.get('id')
                perfil=Perfil.objects.get(id=int(perfil))
                dicci["perfil"]=perfil
            return render(request,'mostrarInfo.html',dicci)
        else:
            vencid=Capitulo.objects.filter(libro=elLibro)
            new=True
            vencido=False
            if len(vencid)!=0:
                venci=vencid[0]
                new=False
                print('CAPITULO:', venci)
                vencimiento=venci.vencimiento.strftime("%Y/%m/%d")
                print("Vencimiento:" + vencimiento)
                hoy=datetime.datetime.now().strftime("%Y/%m/%d")
                print("hoy:", hoy)
                vencido=vencimiento<hoy
                print("VENCIDO: ", vencido)
            pdf=elLibro.titulo.replace(" ","_") +"-" +elLibro.autor.nombre.replace(" ","_")
            dicci={"libro":elLibro,"portada":portada,"calificacion":calificacionF,"pdf":pdf,"fav":fav,"vencido":vencido,"new":new,"comentarios":comentarios,"comentado":comentado,"calificaciones":calificaciones,"calificado":calificado,"califico":califico,"miCali":miCali,"leyo":leyo}
            if(request.user.is_staff==0):
                perfil=request.session.get('id')
                perfil=Perfil.objects.get(id=int(perfil))
                dicci["perfil"]=perfil
            return render(request,'mostrarInfo.html',dicci)
    else:
        return redirect('/')

def impTodo(algo):
    for each in algo:
        print("----------------")
        print(each.isbn)
        print(each.capitulado)
        print("-----------------")

@login_required
def modificarFavoritos(request):
    usu=Perfil.objects.get(id=request.session.get("id"))
    elLibro=Favorito.objects.filter(user=usu,libro_id=request.POST["id"])
    print(len(elLibro))
    if len(elLibro)==0:
        book=Libro.objects.get(id=request.POST["id"])
        usuario=Perfil.objects.get(id=request.session.get("id"))
        nuevo=Favorito(user=usuario,libro=book)
        nuevo.save()
        fav=True
    else:
        elLibro.delete()
        fav=False
    book=Libro.objects.get(id=request.POST['id'])
    unIsbn= str(book.isbn)
    unaDireccion = "/mostrarInfoLibro/?isbn=" + unIsbn

    return redirect(unaDireccion)

@login_required
def verFavoritos(request):
    usu=Perfil.objects.get(id=request.session.get("id"))
    favs=Favorito.objects.filter(user=usu)
    print(favs)
    libros=[]
    claves=[]
    if len(favs)!=0:
        for each in favs:
            aux=Libro.objects.get(id=each.libro_id)
            autor=Autor(nombre=aux.autor.nombre)
            autor2=Autor(nombre=aux.autor.nombre)
            nuevo=Libro(id=aux.id,titulo=aux.titulo,capitulado=aux.capitulado,autor=autor,isbn=aux.isbn)
            nuevo2=Libro(id=aux.id,titulo=aux.titulo,capitulado=aux.capitulado,autor=autor2,isbn=aux.isbn)
            libros.append(nuevo)
            claves.append(nuevo2)

        for each in claves:
            each.titulo=each.titulo.replace(" ","_")
            each.autor.nombre=each.autor.nombre.replace(" ","_")

        dicci={"libros":libros,"libros2":claves,"hay":True}
        print(libros)
        print(claves)
        if(request.user.is_staff==0):
            perfil=request.session.get('id')
            perfil=Perfil.objects.get(id=int(perfil))
            dicci["perfil"]=perfil
        return render(request,'favoritos.html',dicci)
    else:
        dicci={"hay":False}
        if(request.user.is_staff==0):
            perfil=request.session.get('id')
            perfil=Perfil.objects.get(id=int(perfil))
            dicci["perfil"]=perfil
        return render(request,'favoritos.html',dicci)

@login_required
def historial(request):

    usu=Perfil.objects.get(id=request.session.get("id"))
    busquedas=Busqueda.objects.filter(quien=usu)
    histo=[]
    for i in range(len(busquedas)-1,-1,-1):
        print(i)
        histo.append(busquedas[i])
    dicci={'busquedas':histo}
    if(request.user.is_staff==0):
        perfil=request.session.get('id')
        perfil=Perfil.objects.get(id=int(perfil))
        dicci["perfil"]=perfil
    return render(request,'historial.html',dicci)


def proprobando(request):

    book=Libro.objects.get(id=6)
    return render(request,'probando.html',{"t":book})

@login_required
def limpiarHistorial(request):
    usu=Perfil.objects.get(id=request.session.get("id"))
    busquedas=Busqueda.objects.filter(quien=usu)
    busquedas.delete()
    return redirect ('/historial/')

@login_required
def verDetalleNovedad(request):
    if request.method=='GET':
        idNov=request.GET["nov"]
        nov= Novedad.objects.get(id=idNov)
        dicci={'nov':nov,}
        if(request.user.is_staff==0):
            perfil=request.session.get('id')
            perfil=Perfil.objects.get(id=int(perfil))
            dicci["perfil"]=perfil
        return render(request,'detalleNovedad.html',dicci)


@login_required
def pasar_a_premium(request):
    usuario=Usuario.objects.get(user_id=request.user.id)
    cuantos=Perfil.objects.filter(usuario=usuario)
    if (len(cuantos) == 2):
        usuario.tipo=Precio.objects.get(tipo='Premium')
        usuario.save()
        dicci={"usu":usuario,"error":"¡Felicitaciones. Ahora eres un Usuario Premium!"}
        if(request.user.is_staff==0):
            perfil=request.session.get('id')
            perfil=Perfil.objects.get(id=int(perfil))
            dicci["perfil"]=perfil
        return render(request,'miperfil.html',dicci)
    else:
        dicci={"usu":usuario,"error":"Lo sentimos, pero debes tener dos perfiles creados para cambiar tu suscripcion a Usuario Premium."}
        if(request.user.is_staff==0):
            perfil=request.session.get('id')
            perfil=Perfil.objects.get(id=int(perfil))
            dicci["perfil"]=perfil
        return render(request,'miperfil.html',dicci)

@login_required
def dejar_de_ser_premium(request):
    usuario=Usuario.objects.get(user_id=request.user.id)
    cuantos=Perfil.objects.filter(usuario=usuario)
    usuario.tipo=Precio.objects.get(tipo='Comun')
    usuario.save()
    if(len(cuantos) == 4):                          #si tiene 4 perfiles activos se borran los 2 ultimos perfiles
        perfilesborrados = cuantos.last()
        perfilesborrados.delete()
        cuantos=Perfil.objects.filter(usuario__id=usuario.id)           #vuelvo a hacer el query para obtener el ultimo elemento
        perfilesborrados = cuantos.last()
        perfilesborrados.delete()
        dicci={"usu":usuario,"error":"Su suscripcion cambio a Usuario Común. Se eliminaron los dos ultimo perfiles creados"}
        if(request.user.is_staff==0):
            perfil=request.session.get('id')
            perfil=Perfil.objects.get(id=int(perfil))
            dicci["perfil"]=perfil
        return render(request,'miperfil.html',dicci)
    else:
        if(len(cuantos) == 3):                  # si tiene 3 perfiles activos se borra el ultimo perfil
            perfilesborrados = cuantos.last()
            perfilesborrados.delete()
            dicci={"usu":usuario,"error":"Su suscripcion cambio a Usuario Común. Se eliminó el ultimo perfil creado"}
            if(request.user.is_staff==0):
                perfil=request.session.get('id')
                perfil=Perfil.objects.get(id=int(perfil))
                dicci["perfil"]=perfil
            return render(request,'miperfil.html',dicci)
        dicci={"usu":usuario,"error":"Su suscripcion cambio a Usuario Común"}
        if(request.user.is_staff==0):
            perfil=request.session.get('id')
            perfil=Perfil.objects.get(id=int(perfil))
            dicci["perfil"]=perfil
        return render(request,'miperfil.html',dicci)

@login_required
def borrar_perfil(request):
    usu=Usuario.objects.get(user=request.user)
    perfiles=Perfil.objects.filter(usuario=usu)
    post=int(request.POST["id"])
    per=int(request.session.get("id"))
    esSession=post==per
    print("EL POST ES",request.POST["id"])
    print("EL SESSION ES",request.session.get("id"))
    print("ES SESSION====??? ", esSession)
    if usu.tipo.id==2:
        perf=Perfil.objects.get(id=request.POST["id"])
        perf.delete()
        if len(perfiles)<2:
            usu.tipo=Precio.objects.get(id=1)
            usu.save()
    else:
        if len(perfiles)>1:
            perf=Perfil.objects.get(id=request.POST["id"])
            perf.delete()
    if(esSession):
        return redirect('/logout/')
    else:
        return redirect('/miperfil/nuevoPerfil/')

@login_required
def leer(request):
    idLibro=request.GET["libro"]
    cap=request.GET["numero"]
    portada=request.GET["portada"]
    usu=Perfil.objects.get(id=request.session.get("id"))
    libro=Libro.objects.get(id=idLibro)
    if usu.id != 1:
        nuevo=Lectura()
        nuevo.isbn=libro.isbn
        nuevo.titulo=libro.titulo
        nuevo.autor=str(libro.autor)
        nuevo.fecha=datetime.datetime.now()
        nuevo.capitulo=int(cap)
        nuevo.usuario=usu
        print(nuevo)
        nuevo.save()
    link="http://localhost:8001/Plantillas/pdf/"
    link= link + str(portada)
    if (cap!="0"):
        link=link + "-Capitulo" + cap
    link= link + ".pdf#toolbar=0"
    print(link)
    return redirect(link)

def agregarComentario(request):
    unComentario=request.GET["texto"]
    unIsbn= request.GET["isbn"]
    unUsuario=Perfil.objects.get(id=request.session.get("id"))

    unLibro=Libro.objects.get(isbn=int(request.GET["isbn"]))

    unaInstanciaComentario = Comentario(texto=unComentario,autor=unUsuario,libro=unLibro)
    unaInstanciaComentario.save()

    unaDireccion = "/mostrarInfoLibro/?isbn=" + unIsbn

    return redirect(unaDireccion)

def eliminarComentario(request):
    unIsbn= request.GET["isbn"]
    unID = request.GET["id"]
    unComentarioParaEliminar = Comentario.objects.get(id=unID)
    unComentarioParaEliminar.delete()

    unaDireccion = "/mostrarInfoLibro/?isbn=" + unIsbn

    return redirect(unaDireccion)

def agregarCalificacion(request):
    unIsbn= int(request.GET["isbn"])
    unPerfil=Perfil.objects.get(id=request.session.get("id"))
    num = int(request.GET["numero"])
    unLibro=Libro.objects.get(isbn=unIsbn)
    leido = Lectura.objects.filter(isbn=unIsbn,usuario=unPerfil)
    qua = Calificacion.objects.filter(autor=unPerfil,libro=unLibro)
    if (len(leido) > 0):            #si leyó el libro crea la calificación, sino no
        if (len(qua)>0):
            print("Ya habia votado")            #si ya calificó el libro previamente
            cal = Calificacion.objects.get(autor=unPerfil,libro=unLibro)         #se borra la calificacion
            cal.delete()
        else:
            print("No habia votado")
        cali = Calificacion(cuanto = num, autor = unPerfil, libro = unLibro)
        cali.save()
    else:
        print("No lo leyo")
    direc = "/mostrarInfoLibro/?isbn=" + str(unIsbn)
    return redirect(direc)

@login_required
def historialLectura(request):
    usu=Perfil.objects.get(id=request.session.get("id"))
    print(usu)
    lecturas2=Lectura.objects.filter(usuario=usu)
    print(lecturas2)
    lecturas=[]
    for i in range(len(lecturas2)-1,-1,-1):
        print(i)
        lecturas.append(lecturas2[i])
    print(lecturas)
    dicci={'lecturas':lecturas}
    if(request.user.is_staff==0):
        perfil=request.session.get('id')
        perfil=Perfil.objects.get(id=int(perfil))
        dicci["perfil"]=perfil
    return render(request,'historialLectura.html',dicci)

@login_required
def eliminarMiCuenta(request):
    if request.method=="POST":
        intext=request.POST["password"]
        intext=intext.strip()
        if(intext==""):
            if(request.user.is_staff==0):
                perfil=request.session.get('id')
                perfil=Perfil.objects.get(id=int(perfil))
            return render (request,'eliminarMiCuenta.html',{"cod":1,"perfil":perfil})
        else:
            if(intext == request.user.password):
                user=request.user
                do_logout(request)
                user.delete()
                return redirect('/')
            else:
                if(request.user.is_staff==0):
                    perfil=request.session.get('id')
                    perfil=Perfil.objects.get(id=int(perfil))
                return render (request,'eliminarMiCuenta.html',{"cod":2,"perfil":perfil})
    else:
        if(request.user.is_staff==0):
            perfil=request.session.get('id')
            perfil=Perfil.objects.get(id=int(perfil))
        return render (request,'eliminarMiCuenta.html',{"perfil":perfil})

@staff_member_required
def informes(request):
    return render(request,'informes.html')

@staff_member_required
def informeUsuarios(request):
    class informeDeUsuario:
        username=''
        idUsuario=''
        fecha=''
        dni=''

    fechaIni=''
    fechaFin=''

    if request.method=='POST':
        fechaIni= request.POST['fechaDesde']
        fechaFin= request.POST['fechaHasta']
        if (fechaFin<fechaIni):
            usus=Usuario.objects.all()
            usuarios=[]
            for each in usus:
                nue=informeDeUsuario()
                nue.username=each.user.username
                nue.idUsuario=each.id
                nue.fecha=each.user.date_joined.strftime("%Y-%m-%d")
                nue.dni=each.dni
                usuarios.append(nue)
            return render(request,'informeUsuarios.html',{"usuarios":usuarios,"error":True,"fechaInicio":request.POST['fechaDesde'],"fechaFinal":request.POST['fechaHasta']})

        usus=Usuario.objects.all()
        usuarios=[]
        for each in usus:
            fecha=each.user.date_joined.strftime("%Y-%m-%d")
            if (fecha>=fechaIni):
                if (fecha<= fechaFin):
                    nue=informeDeUsuario()
                    nue.username=each.user.username
                    nue.idUsuario=each.id
                    nue.fecha=fecha
                    nue.dni=each.dni
                    usuarios.append(nue)
        return render(request,'informeUsuarios.html',{"usuarios":usuarios,"fechaInicio":request.POST['fechaDesde'],"fechaFinal":request.POST['fechaHasta']})
    else:
        usus=Usuario.objects.all()
        usuarios=[]
        for each in usus:
            nue=informeDeUsuario()
            nue.username=each.user.username
            nue.idUsuario=each.id
            nue.fecha=each.user.date_joined.strftime("%Y-%m-%d")
            nue.dni=each.dni
            usuarios.append(nue)
        return render(request,'informeUsuarios.html',{"usuarios":usuarios})


@staff_member_required
def informeLibros(request):
    lecturas=Lectura.objects.all()
    libros=Libro.objects.all()
    class informeDeLibro:
        isbn=''
        idLibro=''
        cant=''
        titulo=''
        autor=''

        def _str_(self):
            cadena="Mi isbn es " + str(self.isbn) + ", mi id es " + str(self.idLibro) + ", mi titulo es " + str(self.titulo) + ", mi autor es " + str(self.autor) + " y mi cantidad es " + str(self.cant)
            return cadena

    cantidades=[]
    if len(libros)>0:
        for each in lecturas:
            nono=True
            for c in cantidades:
                if (each.isbn == c.isbn):
                    nono=False
                    break
            if(nono):
                if len(Libro.objects.filter(isbn=each.isbn))>0:
                    lec=informeDeLibro()
                    lec.isbn=each.isbn
                    lec.idLibro=Libro.objects.get(isbn=each.isbn).id
                    lec.titulo=Libro.objects.get(isbn=each.isbn).titulo
                    lec.autor=Libro.objects.get(isbn=each.isbn).autor
                    cant=1
                    people=[]
                    people.append(each.usuario)
                    for each2 in lecturas:
                        if (each.isbn == each2.isbn):
                            if each2.usuario not in people:
                                cant= cant + 1
                                people.append(each2.usuario)
                    lec.cant=cant
                    cantidades.append(lec)
        for each in libros:
            noEsta=True
            for each2 in cantidades:
                if( each2.isbn == each.isbn ):
                    noEsta=False
                    break
            if (noEsta):
                lec=informeDeLibro()
                lec.isbn=each.isbn
                lec.idLibro=Libro.objects.get(isbn=each.isbn).id
                lec.titulo=Libro.objects.get(isbn=each.isbn).titulo
                lec.autor=Libro.objects.get(isbn=each.isbn).autor
                lec.cant=0
                cantidades.append(lec)
        ordenados= sorted(cantidades,reverse=True,key=lambda libro : libro.cant )
    else:
        ordenados=[]
    return render (request,'informeLibros.html',{"libros":ordenados})
