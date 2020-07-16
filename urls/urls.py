"""Ingenieria URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from bookflix.views import holaMundo, holaMundoTemplate
from bookflix.views import resultadosBusqueda,emptyPath,login,registrame,signIn,logout,register_profile,miperfil,home,mostrarInfoLibro,modificarFavoritos,verFavoritos,historial,proprobando, limpiarHistorial, verDetalleNovedad
from bookflix.views import pasar_a_premium,borrar_perfil,dejar_de_ser_premium,leer,agregarComentario,eliminarComentario,eliminarMiCuenta,historialLectura,informes,informeLibros,informeUsuarios
from bookflix.views import elegirPerfil,setPerfil,agregarCalificacion


urlpatterns = [
    path('admin/', admin.site.urls),
    path('holaMundo/',holaMundo),
    path('holaMundoTemplate/',holaMundoTemplate),
    path('admin/informes/', informes),
    path('admin/informes/Usuarios', informeUsuarios),
    path('admin/informes/Libros', informeLibros),
    path('resultadosBusqueda/', resultadosBusqueda),
    path('',emptyPath),
    path('logout/',logout),
    path('login/',login),
    path('elegirPerfil/',elegirPerfil),
    path('setPerfil/',setPerfil),
    path('sign_in/',signIn),
    path('registrame/',registrame),
    path('miperfil/nuevoPerfil/',register_profile),
    path('miperfil/',miperfil),
    path('home/',home),
    path('mostrarInfoLibro/',mostrarInfoLibro),
    path('mOdIfYFavoRit0/',modificarFavoritos),
    path('favoritos/',verFavoritos),
    path('historial/',historial),
    path('informes/',proprobando),
    path('limpiarHistorial/',limpiarHistorial),
    path('verDetalleNovedad/',verDetalleNovedad),
    path('pasateapremium/',pasar_a_premium),
	path('borrarPerfil/',borrar_perfil),
    path('dejardeserpremium/',dejar_de_ser_premium),
    path('l3er/',leer),
    path('agregarComentario/',agregarComentario),
    path('eliminarComentario/',eliminarComentario),
    path('agregarCalificacion/',agregarCalificacion),
    path('eliminarMiCuenta/',eliminarMiCuenta),
    path('historialLectura/',historialLectura),
]

admin.site.site_header = 'Administracion Bookflix'
