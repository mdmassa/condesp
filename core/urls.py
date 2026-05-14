from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('biblioteca/', views.biblioteca, name='biblioteca'),
    path('upload_document/', views.upload_document, name='upload_document'),
    path('edit_document/', views.edit_document, name='edit_document'),
    path('delete_document/', views.delete_document, name='delete_document'),
    path('buscar/', views.buscar_elementos, name='buscar_elementos'),
    path('exportar/', views.exportar_elementos, name='exportar_elementos'),
    path('upload/', views.upload_planilha, name='upload'),
    path('editar/<int:pk>/', views.edit_descricao, name='edit_descricao'),
    path('deletar/<int:pk>/', views.deletar_elemento, name='deletar_elemento'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
