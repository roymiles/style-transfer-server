from django.urls import path

from . import views

urlpatterns = [
    # Shows the stylised images in a collage
    path('collage/', views.collage, name='collage'),

    # Route for uploading images
    path('upload/', views.upload, name='upload'),
]