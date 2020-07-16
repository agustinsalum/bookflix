from django.contrib.auth.forms import UserCreationForm
from django import forms 
from django.contrib.auth.models import User
from .models import Perfil, Tarjeta,Precio,Usuario

class UserCreationFormExtends(UserCreationForm):
    email = forms.EmailField(label="Correo electrónico")
    first_name = forms.CharField(label="Nombre")
    last_name = forms.CharField(label="Apellido")



    class Meta:
        model = User
        fields = ["username", "password1", "password2","email","first_name","last_name",]

class UserEditForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, label='Nombre')
    last_name = forms.CharField(required=True, label='Apellido')

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]
        exclude = ('username',)


class ProfileCreateForm(forms.ModelForm):
    nom =forms.CharField(required=True, label="Nombre")

    
    class Meta:
        model = Perfil
        fields = [
            "nom"
        ]
        exclude = ('usuario', 'fecha')

class UsuarioCreacionForm(forms.ModelForm):
    dni=forms.IntegerField(required=True,label="DNI")
    nacimiento=forms.DateField(required=True,label="Fecha de Nacimiento",input_formats=['%d-%m-%Y'],help_text="Fecha de nacimiento")
    
    class Meta:
        model = Usuario
        fields = [
            "dni","nacimiento"
        ]
        exclude = ("user", "tarjeta","tipo")

class TarjetaCreacionForm(forms.ModelForm):
    num=forms.IntegerField(required=True,max_value=9999999999999999)
    cod=forms.IntegerField(required=True,max_value=9999)
    nom=forms.CharField(required=True,label="Nombre")
    venc=forms.DateField(required=True,input_formats=['%m-%Y'])

    class Meta:
        model = Tarjeta
        fields = [
            "num","cod","nom","venc"
        ]
