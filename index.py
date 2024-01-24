from flask import Flask, request, jsonify,send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import numpy as np
import requests
import shutil
import cv2
import os


app = Flask(__name__)
secret = os.getenv('key')
micro = os.getenv('microsoft')
@app.route('/')
def home():
    return "secret"

def process_image(peturl,PETS_NAME):
    data = {'url': peturl}
    headers = {
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': f'{micro}',
    }
    endpoint = "https://instance098098098.cognitiveservices.azure.com/"
    service_url = 'computervision/imageanalysis:segment?api-version=2023-02-01-preview&mode=backgroundRemoval'
    url = endpoint + service_url
    response = requests.post(url, headers=headers,json=data)
    img = Image.open(BytesIO(response.content))

    width, height = img.size
    np_img = np.array(img)
    mask = np_img[:,:,3]
    rgba_mask = cv2.merge([mask,mask,mask,np.ones(mask.shape).astype('uint8')])
    rgba_mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGBA )
    ret,thresh = cv2.threshold(mask,127,255,0)
    contours, _ = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cnt = contours[0]
    x,y,w,h = cv2.boundingRect(cnt)
    cimg = cv2.drawContours(cv2.merge([mask,mask,mask]),[cnt],0,(0,255,255),2)
    cimg = cv2.rectangle(cimg,(x,y),(x+w,y+h),(0,255,0),2)
    crop_img = np_img[y:y+h, x:x+w]
    pet = Image.fromarray(crop_img)

    frame = Image.open('frame.png').convert("RGBA")
    collage_width = 191
    xstart = 208
    collage_height = 265
    fw,fh = frame.size
    w,h = pet.size
    pet_h = collage_width
    factor = collage_width/ w
    newsize = (pet_h, int(h*factor))

    bottom_line = 551
    pet_r = pet.resize(newsize)


    ystart = bottom_line - newsize[1]
    if (newsize[1] > collage_height):
        pet_r = pet_r.crop((0,0,pet_r.size[0],collage_height))
        ystart = bottom_line - pet_r.size[1]

    Image.Image.paste(frame,pet_r, (xstart,ystart ))

    text_size = 48
    top_text_x = 148
    draw = ImageDraw.Draw(frame)
    font = ImageFont.truetype("Roboto-Regular.ttf", size=text_size)
    _, _, w, h = draw.textbbox((0, 0), PETS_NAME, font=font)
    while (w > 363):
        text_size -=1
        font = ImageFont.truetype("Roboto-Regular.ttf", size=text_size)
        _, _, w, h = draw.textbbox((0, 0), PETS_NAME, font=font)
    draw.text(((fw-w)/2, top_text_x), PETS_NAME, font=font, fill="black")
    #frame.save("export.png", format='PNG')
    return frame


@app.route('/image')
def index():
    headers = request.headers
    auth = headers.get("Key")
    if auth ==secret:
        data = request.json
        url = data['url']
        pet_name = data['pet_name']
        frame = process_image(url,pet_name)
        output = BytesIO()
        frame.convert('RGBA').save(output, format='PNG')
        output.seek(0, 0)
        return send_file(output, mimetype='image/png', as_attachment=False)
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401