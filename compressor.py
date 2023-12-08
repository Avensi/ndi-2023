from flask import Flask, send_file, request
import requests
import os
from PIL import Image
from flask_cors import CORS
import os

app = Flask('compressor')
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


img_path = os.path.join('temp', 'temp.png')
img_destination_path = os.path.join('temp', 'temp.webp')
@app.route("/sanity_check")
def sanity_check():
    return "Hello World!"

@app.route("/img/<int:size>/<path:url>")
def img(size,url):
    try:
        res = compress_img(max_size=size, url=url)
        send_file(img_destination_path, as_attachment=True)
        return res

    except Exception as e:
        return str(e)

def compress_img(max_size, url):

    download_image(url, file_path=img_path)
    compress_to_ideal(max_size=max_size,file_path=img_path, destination_path=img_destination_path)

    return return_image_result(file_path=img_path, destination_path=img_destination_path)

def download_image(url, file_path): 
    response = requests.get(url, stream=True)
    response.raw.decode_content = True
    with open(file_path, mode="wb") as file:
        file.write(response.content)

def get_size_of_image(file_path):
    return os.stat(file_path).st_size / 1000

def compress_to_ideal(max_size, file_path, destination_path): 
    quality = 100
    image = Image.open(file_path)
    image.save(destination_path, format="webp", optimize=True, quality=quality)
    while get_size_of_image(destination_path) > max_size and quality > 0:
            quality -= 10 
            image.save(destination_path, format="webp", optimize=True, quality=quality)
            if quality <= 0 : 
                return False
    return True

def return_image_result(file_path, destination_path):
    current = Image.open(file_path)
    res = Image.open(destination_path)

    return {
        'new_url':'',
        'og_size': current.size,
        'og_weight': f'{get_size_of_image(file_path)} KB' ,
        'og_format': current.format,
        'new_size' : res.size,
        'new_weight': f'{get_size_of_image(destination_path)} KB' ,
        'new_format': res.format
    }