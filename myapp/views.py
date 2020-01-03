from django.http import HttpResponse
from myapp.utils import load_img, tensor_to_image, make_collage
import tensorflow as tf
import tensorflow_hub as hub
from django.http import HttpResponseRedirect
from django.template import Context, Template
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import uuid
import os
from random import shuffle


def collage(request):
    # Make collage
    filenames = []
    for file in os.listdir("myapp/static/content-images/"):
        if file.endswith((".png", ".jpg", ".jpeg")):
            filenames.append(file)

    print(f"Making collage with the following files: {filenames}")
    shuffle(filenames)
    filenames = [f"myapp/static/content-images/{name}" for name in filenames]

    unique_collage_name = str(uuid.uuid1())
    make_collage(images=filenames,
                 filename=f"myapp/static/content-collages/{unique_collage_name}.png",
                 width=500,
                 init_height=100)

    content_image = load_img(f"myapp/static/content-collages/{unique_collage_name}.png")

    styles = ["van_gogh.jpg", "matrix.png", "matrix2.jpg", "style1.jpg"]
    style_image = load_img(f"myapp/static/style-images/{styles[2]}")

    unique_stylised_collage_name = str(uuid.uuid1())
    hub_module = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/1')
    stylized_image = hub_module(tf.constant(content_image), tf.constant(style_image))[0]
    out_image = tensor_to_image(stylized_image)
    out_image.save(f"myapp/static/output-images/{unique_stylised_collage_name}.png")

    return render(request, 'collage.html', {'collage_link': f"output-images/{unique_stylised_collage_name}.png"})


def upload(request):
    if request.method == 'POST':
        """ Handle the file upload request """
        image = request.FILES['image']

        _, ext = os.path.splitext(image.name)

        if ext not in [".jpeg", ".jpg", ".png"]:
            return HttpResponse(f"Invalid image file extension - {ext}")

        unique_name = str(uuid.uuid1())
        fs = FileSystemStorage()

        filename = fs.save(f"myapp/static/content-images/{unique_name}.{ext}", image)
        uploaded_file_url = fs.url(filename)

        return HttpResponseRedirect('/collage')
    else:
        """ Display the upload form """
        return render(request, 'upload.html')
