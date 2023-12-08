from flask import Flask, send_file, request
import requests
import os
from PIL import Image
from flask_cors import CORS

app = Flask('compressor')
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


temp_folder_name = 'temp'

@app.route("/")
def sanity_check():
    return "Hello, this is image compressor !"

@app.route("/img/<int:size>/<path:url>")
def img(size,url):
    try:
        return compress_img(max_size=size, url=url)

    except Exception as e:
        return str(e)
    
@app.route("/res_img/<path:url>")
def img_res(url): 
    img_destination_path = os.path.join(temp_folder_name, f'{get_filename(url)[:-4]}.webp')
    return send_file(img_destination_path, as_attachment=True)

def get_filename(url): 
    return url.split('/')[-1]

def compress_img(max_size, url):
    file_path = os.path.join(temp_folder_name, get_filename(url))
    img_destination_path = os.path.join(temp_folder_name, f'{get_filename(url)[:-4]}.webp')
    download_resource(url, file_path=file_path)
    compress_to_ideal(max_size=max_size,file_path=file_path, destination_path=img_destination_path)

    return return_image_result(file_path=file_path, destination_path=img_destination_path, url=url)

def download_resource(url, file_path): 
    response = requests.get(url, stream=True)
    response.raw.decode_content = True
    with open(file_path, mode="wb") as file:
        file.write(response.content)

def remove_resource(file_path):
    os.remove(file_path)

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

def return_image_result(file_path, destination_path, url):
    current = Image.open(file_path)
    res = Image.open(destination_path)

    return {
        'new_url':f'{request.url_root}res_img/{url}',
        'og_size': current.size,
        'og_weight': f'{get_size_of_image(file_path)} KB' ,
        'og_format': current.format,
        'new_size' : res.size,
        'new_weight': f'{get_size_of_image(destination_path)} KB' ,
        'new_format': res.format
    }

