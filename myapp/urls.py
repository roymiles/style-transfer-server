from django.urls import path

from . import views

urlpatterns = [
    # Shows the stylised images in a collage
    path('', views.result, name='result'),

    # Route for uploading images
    path('upload/', views.upload, name='upload'),

    # Utility route for ajax
    path('get_styled_images', views.get_styled_images, name='get_styled_images'),
]