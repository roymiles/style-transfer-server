from django.http import HttpResponse
from myapp.utils import load_img, tensor_to_image
import tensorflow as tf
import tensorflow_hub as hub
from django.http import HttpResponseRedirect
from django.template import Context, Template
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import uuid


def collage(request):
    content_image = load_img("myapp/static/content-images/dog.jpg")
    style_image = load_img("myapp/static/style-images/van_gogh.jpg")

    hub_module = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/1')
    stylized_image = hub_module(tf.constant(content_image), tf.constant(style_image))[0]
    out_image = tensor_to_image(stylized_image)
    out_image.save("output.jpg")

    return render(request, 'collage.html', {'collage_link': "output.jpg"})


def upload(request):
    print(request)
    if request.method == 'POST' and request.FILES['image']:
        """ Handle the file upload request """
        image = request.FILES['image']
        image.name = uuid.uuid1()
        fs = FileSystemStorage()

        filename = fs.save("myapp/static/content-images/" + image.name, image)
        uploaded_file_url = fs.url(filename)

        return HttpResponseRedirect('/collage')
    else:
        """ Display the upload form """
        return render(request, 'upload.html')
