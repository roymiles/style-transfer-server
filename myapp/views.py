from django.http import HttpResponse, JsonResponse
from myapp.utils import load_img, tensor_to_image
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
import re

# Removing warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.getLogger('tensorflow').disabled = True

BASE_DIR = settings.BASE_DIR


def static_path(rel_path):
    return os.path.join(BASE_DIR, "myapp", "static", "media", rel_path)


def result(request):
    # Show content, styles and outcome/result in a table
    results = _styled_images()
    return render(request, 'result.html', {"results": results})


def _styled_images():
    """
        Utility function
    """
    results = {}
    key = 0
    for file in reversed(os.listdir(static_path("styled-images"))):

        if key == 10:
            break

        if file.endswith((".png", ".jpg", ".jpeg")):
            # styled-images filenames will have format {id}_{style}.png
            idx, extra = file.split("_")
            style, ext = extra.split(".")
            entry = dict()
            entry["content"] = f"{idx}.png"
            entry["style"] = f"{style}.png"
            entry["result"] = file
            results[str(key)] = entry
            key += 1

    return results


def get_styled_images(request):
    """
        Return top-n images
    """
    results = _styled_images()
    return JsonResponse(results)


def upload(request):
    if request.method == 'POST':
        """ Handle the file upload request """
        _, ext = os.path.splitext(request.FILES['image'].name)

        if ext not in [".jpeg", ".jpg", ".png"]:
            return HttpResponse(f"Invalid image file extension - {ext}")

        try:
            # Open, modify and then save in memory
            img = Image.open(request.FILES['image'])
            img.thumbnail((256, 256), Image.ANTIALIAS)
            thumb_io = BytesIO()
            img_format = str(request.FILES['image'].content_type.split('/')[-1].upper())
            img.save(thumb_io, img_format)

            # Generating name for the new file (always save as png for simplicity)
            new_file_name = 'image_' + str(int(time.time())) + ".png"

            # Creating new InMemoryUploadedFile() based on the modified file
            resized_image = InMemoryUploadedFile(thumb_io,
                                                 u"image",  # Important to specify field name here
                                                 new_file_name,
                                                 request.FILES['image'].content_type,
                                                 thumb_io.getbuffer().nbytes,
                                                 None)

            # and finally, replacing original InMemoryUploadedFile() with modified one
            # request.instance.image = file

        except:
            return HttpResponse(f"Unable to parse image.")

        unique_name = datetime.now().strftime("%Y%m%d-%H%M%S")
        fs = FileSystemStorage()

        unique_path = static_path(os.path.join("content", f"{unique_name}.png"))
        filename = fs.save(unique_path, resized_image)
        uploaded_file_url = fs.url(filename)

        # === Generate stylised image === #
        # Choose a random style
        styles = ["warsaw.png", "vangogh.png", "alexgrey.png", "starrynight.png"]
        random_style = random.choice(styles)
        style_image = load_img(static_path(os.path.join("styles", f"{random_style}")))
        style_name = random_style.split('.')[0]  # van_gogh, warsaw etc

        content_image = load_img(unique_path)
        hub_module = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
        stylized_image = hub_module(tf.constant(content_image), tf.constant(style_image))[0]
        out_image = tensor_to_image(stylized_image)
        output_path = static_path(os.path.join("styled-images", f"{unique_name}_{style_name}.png"))
        print(f"Saving to: {output_path}")
        out_image.save(output_path)

        # Delete oldest content/images?

        return HttpResponseRedirect('/')

    else:
        """ Display the upload form """
        return render(request, 'upload.html')
