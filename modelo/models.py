from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
# Create your models here.
class Tarjeta(models.Model):
    num=models.CharField(blank=False, null=False, max_length=16)
    cod=models.IntegerField(blank=False, null=False)
    nom=models.CharField(max_length=30,blank=False,verbose_name='Nombre')
    venc=models.DateField(blank=False,null=True,verbose_name='Fecha')

    def __str__(self):
        cadena=str(self.num)
        return cadena

class Precio(models.Model):
    fecha=models.DateField(blank=False,null=True,verbose_name='Fecha')
    tipo=models.CharField(max_length=250,verbose_name='Tipo')
    costo=models.IntegerField(blank=False,null=True,verbose_name='Costo')

    def __str__(self):
        cadena=self.tipo
        return cadena

class Usuario(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    dni=models.CharField(blank=False, unique=True, max_length=8,verbose_name='DNI')
    nacimiento=models.DateField(blank=False,null=True,verbose_name='Nacimiento')
    tarjeta=models.ForeignKey(Tarjeta, on_delete=models.SET_NULL, blank=False, null=True, verbose_name='Tarjeta de Credito')
    tipo=models.ForeignKey(Precio,on_delete=models.SET_NULL,null=True)

    def __str__(self):
        cadena=self.user.username
        return cadena

    def clean(self, *args, **kwargs):
        # run the base validation
        super(Usuario, self).clean(*args, **kwargs)

        # Don't allow dates older than now.
        print('Nacimiento:' , self.nacimiento)
        now= datetime.datetime.now()
        valid= now - datetime.timedelta(days=6570)
        autorizado= valid.strftime("%Y/%m/%d")

        print('Minimo:', autorizado)
        nacimiento=self.nacimiento.strftime("%Y/%m/%d")
        if nacimiento > autorizado:
            raise ValidationError('La persona debe ser mayor de edad')

class Perfil(models.Model):
    usuario=models.ForeignKey(Usuario, on_delete=models.CASCADE,null=True)
    nom=models.CharField(max_length=15,verbose_name='Nombre')
    fecha=models.DateField(blank=False,null=True,verbose_name='Fecha')
    foto=models.CharField(max_length=50,verbose_name="Foto",null=True)

    def __str__(self):
        cadena=self.nom
        return cadena

    class Meta:
        verbose_name_plural ="Perfiles"

class Editorial(models.Model):
    nombre=models.CharField(max_length=50,blank=False,null=False,verbose_name='Nombre')

    def __str__(self):
        cadena=self.nombre
        return cadena

    class Meta:
        verbose_name_plural ="Editoriales"

class Autor(models.Model):
    nombre=models.CharField(max_length=25,blank=False,null=False,verbose_name='Nombre')
    nacimiento=models.DateField(blank=True,null=True,verbose_name='Fecha de Nacimiento')

    def __str__(self):
        cadena=self.nombre
        return cadena

    class Meta:
        verbose_name_plural ="Autores"

class Genero(models.Model):
    nombre=models.CharField(max_length=250,blank=False,null=False,verbose_name='Nombre')

    def __str__(self):
        cadena=self.nombre
        return cadena

class Novedad(models.Model):
    titulo=models.CharField(max_length=250,blank=False,null=True,verbose_name='Titulo')
    descripcion=models.TextField(validators=[MinLengthValidator(20)],blank=False,null=True,verbose_name='Descripcion')
    fecha=models.DateField(blank=False, null=False, verbose_name='Fecha', default=datetime.date.today)

    def __str__(self):
        cadena=self.titulo
        return cadena

    class Meta:
        verbose_name_plural ="Novedades"

class Libro(models.Model):
    isbn=models.IntegerField(blank=False,null=True,verbose_name='ISBN',unique=True)
    titulo=models.CharField(max_length=250,blank=False,null=False,verbose_name='Titulo')
    trailer=models.TextField(max_length=1000,blank=False,null=False,verbose_name='Trailer')
    portada=models.ImageField(upload_to="Plantillas/Portadas",null=True,height_field=None,width_field=None,max_length=100,verbose_name='Portada')
    capitulado=models.BooleanField(blank=False,null=False,verbose_name='Es Capitulado')
    autor=models.ForeignKey(Autor, on_delete=models.SET_NULL,null=True,blank=False)
    editorial=models.ForeignKey(Editorial, on_delete=models.SET_NULL,null=True,blank=False)
    genero=models.ForeignKey(Genero, on_delete=models.SET_NULL,null=True,blank=False)
    vencimiento=models.DateField(blank=False,null=True,verbose_name='Fecha de Vencimiento')

    def clean(self, *args, **kwargs):
        # run the base validation
        super(Libro, self).clean(*args, **kwargs)

        # Don't allow dates older than now.
        print('Vencimiento:' , self.vencimiento)
        now= datetime.datetime.now()
        ahora= now.strftime("%Y/%m/%d")
        vencimiento= self.vencimiento.strftime("%Y/%m/%d")
        print('Minimo:', ahora)
        if vencimiento < ahora:
            raise ValidationError('La fecha de vencimiento debe ser posterior al dia de hoy.')

    def __str__(self):
        cadena=self.titulo + "  -  " + self.autor.nombre
        return cadena

class Comentario(models.Model):
    texto=models.CharField(max_length=500,blank=False,null=True,verbose_name='Texto')
    autor=models.ForeignKey(Perfil, on_delete=models.CASCADE,null=True)
    libro=models.ForeignKey(Libro,on_delete=models.CASCADE,null=True)

    def __str__(self):
        cadena=self.texto
        return cadena

class Calificacion(models.Model):
    cuanto=models.IntegerField(blank=False,null=True,verbose_name='Valor')
    autor=models.ForeignKey(Perfil, on_delete=models.CASCADE,null=True)
    libro=models.ForeignKey(Libro,on_delete=models.CASCADE,null=True)

    def __str__(self):
        cadena=str(self.cuanto)
        return cadena

    class Meta:
        verbose_name_plural ="Calificaciones"

class Busqueda(models.Model):
    fecha=models.DateField(blank=False,null=True)
    quien=models.ForeignKey(Perfil,on_delete=models.SET_NULL,null=True)
    que=models.CharField(blank=False,null=True,max_length=200)

class Capitulo(models.Model):
    numero=models.IntegerField(null=False,blank=False)
    libro=models.ForeignKey(Libro, on_delete=models.CASCADE,null=False)
    pdf=models.FileField(upload_to='Plantillas/pdf',verbose_name="Archivo PDF",null=False,blank=False)
    vencimiento=models.DateField(blank=False,null=True,verbose_name='Fecha de Vencimiento')


    def __str__(self):
        cadena=str(self.libro.titulo + ": Capitulo ") + str(self.numero)
        return cadena

    def clean(self, *args, **kwargs):
        # run the base validation
        super(Capitulo, self).clean(*args, **kwargs)

        # Don't allow dates older than now.
        print('Vencimiento:' , self.vencimiento)
        now= datetime.datetime.now()
        ahora= now.strftime("%Y/%m/%d")
        vencimiento= self.vencimiento.strftime("%Y/%m/%d")
        print('Minimo:', ahora)
        if vencimiento < ahora:
            raise ValidationError('La fecha de vencimiento debe ser posterior al dia de hoy.')
        #self.numero=86
        if(self.numero>0):
            numeros=Capitulo.objects.filter(libro=self.libro)
            print('Existen ', len(numeros),' capitulos: ',numeros)
            if (len(numeros)!=0):
                ultimo=len(numeros)
            else:
                ultimo=0
            print('La cantidad es ', ultimo)
            if self.numero > ultimo:
                if self.numero != (ultimo + 1):
                    raise ValidationError('Numero de capitulo incorrecto, el nuevo capitulo a subir deberia ser el numero: '+ str(ultimo + 1))
            else:
                repetido=Capitulo.objects.filter(libro=self.libro,numero=self.numero)
                if (len(repetido)==1):
                    repetido=Capitulo.objects.get(libro=self.libro,numero=self.numero)
                    repetido.delete()
        else:
            raise ValidationError('Los numeros de los capitulos no pueden ser menores a 1')

class Favorito(models.Model):
    libro=models.ForeignKey(Libro, on_delete=models.CASCADE,null=False)
    user=models.ForeignKey(Perfil,on_delete=models.SET_NULL,null=True)

class Lectura(models.Model):
    isbn=models.IntegerField(null=False,blank=False,verbose_name='ISBN')
    fecha=models.DateField(blank=False,null=True,verbose_name='Fecha de Lectura')
    titulo=models.CharField(max_length=300, blank=False,null=False,verbose_name='Titulo')
    autor=models.CharField(max_length=300,blank=False,null=False,verbose_name='Autor')
    capitulo=models.IntegerField(null=False,blank=False,verbose_name='Capitulo')
    usuario=models.ForeignKey(Perfil,on_delete=models.CASCADE,null=True)

    def __str__(self):
        cadena="ISBN: " + str(self.isbn) + ", TITULO: " + self.titulo + ", AUTOR: " + self.autor + ", CAPITULO: " + str(self.capitulo)
        return cadena
