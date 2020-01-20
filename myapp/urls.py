from django.urls import path

from . import views

urlpatterns = [
    # Shows the stylised images in a collage
    path('/', views.collage, name='collage'),
    path('collage/', views.collage, name='collage'),

    # Route for uploading images
    path('upload/', views.upload, name='upload'),

    path('collage/get_filename', views.get_collage_filename, name='get_collage_filename'),
]