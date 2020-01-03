from django.http import HttpResponse
from myapp.utils import load_img, tensor_to_image
import tensorflow as tf
import tensorflow_hub as hub
from django.http import HttpResponseRedirect
from django.template import Context, Template
from django.shortcuts import render


def collage(request):
    content_image = load_img("C:\\Users\\Roy\\PycharmProjects\\StyleTransfer\\dog.jpg")
    style_image = load_img("C:\\Users\\Roy\\PycharmProjects\\StyleTransfer\\van_gogh.jpg")

    hub_module = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/1')
    stylized_image = hub_module(tf.constant(content_image), tf.constant(style_image))[0]
    out_image = tensor_to_image(stylized_image)
    out_image.save("output.jpg")

    return HttpResponse("Done")


def upload(request):
    if request.method == 'POST':
        """ Handle the file upload request """
        return HttpResponseRedirect('/collage')
    else:
        """ Display the upload form """
        template = Template("My name is {{ my_name }}.")
        context = Context({"my_name": "Adrian"})
        template.render(context)
        return render(request, 'example.html', {'title': "xdfg", 'cal': "dfgdfg"})
