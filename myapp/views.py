from django.http import HttpResponse
from myapp.utils import load_img, tensor_to_image, make_collage, make_collage_v2
import tensorflow as tf
import tensorflow_hub as hub
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import os
from random import shuffle
from django.conf import settings
import hashlib
from datetime import datetime
import random
import logging
from PIL import Image
import time
from os import path
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO

# Removing warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.getLogger('tensorflow').disabled = True

BASE_DIR = settings.BASE_DIR


def static_path(rel_path):
    return os.path.join(BASE_DIR, f"static/media/{rel_path}")


def collage(request):
    # Sort collages in order and show most recent
    filenames = []
    for file in os.listdir(static_path("styled-collages/")):
        if file.endswith((".png", ".jpg", ".jpeg")):
            filenames.append(file)

    if len(filenames) == 0:
        return HttpResponse(f"No collages have been made.")

    filenames.sort(reverse=True)

    return render(request, 'collage.html', {'collage_link': f"styled-collages/{filenames[0]}"})


def get_collage_filename(request):
    # Sort collages in order and show most recent
    filenames = []
    for file in os.listdir(static_path("styled-collages/")):
        if file.endswith((".png", ".jpg", ".jpeg")):
            filenames.append(file)

    if len(filenames) == 0:
        return HttpResponse(f"No collages have been made.")

    filenames.sort(reverse=True)
    return HttpResponse(f"styled-collages/{filenames[0]}")


def upload(request):
    if request.method == 'POST':
        """ Handle the file upload request """
        _, ext = os.path.splitext(request.FILES['image'].name)

        # Open, modify and then save in memory
        img = Image.open(request.FILES['image'])
        img.thumbnail((256, 256), Image.ANTIALIAS)
        thumb_io = BytesIO()
        img_format = str(request.FILES['image'].content_type.split('/')[-1].upper())
        img.save(thumb_io, img_format)

        # Generating name for the new file
        new_file_name = 'image_' + str(int(time.time())) + ext

        # Creating new InMemoryUploadedFile() based on the modified file
        resized_image = InMemoryUploadedFile(thumb_io,
                                             u"image",  # Important to specify field name here
                                             new_file_name,
                                             request.FILES['image'].content_type,
                                             thumb_io.getbuffer().nbytes,
                                             None)

        # and finally, replacing original InMemoryUploadedFile() with modified one
        # request.instance.image = file

        if ext not in [".jpeg", ".jpg", ".png"]:
            return HttpResponse(f"Invalid image file extension - {ext}")

        unique_name = datetime.now().strftime("%Y%m%d-%H%M%S")
        fs = FileSystemStorage()

        unique_path = static_path(f"content/{unique_name}.{ext}")
        filename = fs.save(unique_path, resized_image)
        uploaded_file_url = fs.url(filename)

        # === Generate stylised image === #
        print("Generating stylised collage...")

        # Choose a random style
        styles = ["warsaw.png", "van_gogh.jpg"]
        style_image = load_img(static_path(f"styles/{random.choice(styles)}"))

        content_image = load_img(unique_path)
        hub_module = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
        stylized_image = hub_module(tf.constant(content_image), tf.constant(style_image))[0]
        out_image = tensor_to_image(stylized_image)
        output_path = static_path(f"styled-images/{unique_name}.png")
        out_image.save(output_path)

        # === Update collage === #
        filenames = []
        for file in os.listdir(static_path("styled-images/")):
            if file.endswith((".png", ".jpg", ".jpeg")):
                filenames.append(file)

        print(f"Making collage with the following files: {filenames}")
        shuffle(filenames)
        filenames = [static_path(f"styled-images/{name}") for name in filenames]
        filenames.sort(reverse=True)  # Ony want first N (names in datetime format)

        # Limit to first N most recent
        n = min(20, len(filenames))
        filenames = filenames[0:n]

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        unique_collage_name = hashlib.md5(''.join(filenames).encode('utf-8')).hexdigest()
        unique_collage_path = static_path(f"styled-collages/{timestamp}_{unique_collage_name}.png")
        print(f"Collage path: {unique_collage_path}")
        """make_collage_v2(
            images=filenames,
            filename=unique_collage_path,
            width=1024,
            init_height=768
        )"""
        make_collage_v2(
            images=filenames,
            filename=unique_collage_path
        )

        return HttpResponseRedirect('/collage')
    else:
        """ Display the upload form """
        return render(request, 'upload.html')