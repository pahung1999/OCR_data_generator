from PIL import Image, ImageDraw, ImageFont
from typing import Tuple
import random
import numpy as np
from tqdm import tqdm
import os
import matplotlib.pyplot as plt
import copy
import cv2
from src.gen_box import gen_imgInteval, random_multi_boxes, box_gen
from src.gen_color import gen_text_color_v2, gen_text_color
from src.fill_text import fill_text_to_image, draw_rectangle
import io
import base64
import json


MAX_SIZE = (2048, 2048)
BOX_SCALE = (0.05, 0.6)
FONT_SIZE_RANGE = (10, 80)
MAX_INTERGRAL = 40
MIN_TEXT_BG_DIFF = 4
MAX_BOXES_PER_IMAGE = 20
MAX_LOOP = 1000

#Just max samples because if can't find a position to place text on background image -> skip
sample_num = 10000

font_dir = "./data/font/"
bg_dir = "./data/background/"

# Labelme Folder (output folder)
labelme_dir = "/home/phung/AnhHung/data/ocr_data/text_on_bg/labelme3/"



def plot_img(img, size=(8, 8)):
    plt.figure(figsize=size)
    plt.imshow(img)
    plt.axis('off')
    plt.show()

#Load font
font_list =[]
for filename in os.listdir(font_dir):
    font = ImageFont.truetype(os.path.join(font_dir, filename), size=50)
    font_list.append(font)



for sample_id in tqdm(range(sample_num)):
    # bg_name = random.choice(os.listdir(bg_dir))
    bg_name = os.listdir(bg_dir)[sample_id%len(os.listdir(bg_dir))]
    bg_path = os.path.join(bg_dir, bg_name)

    PIL_image = Image.open(bg_path)
    PIL_image.thumbnail(MAX_SIZE)
    np_image = np.array(PIL_image)
    w, h = PIL_image.size

    imageIntegral = gen_imgInteval(np_image)

    boxes_dict = random_multi_boxes(image_size = PIL_image.size, 
                    imageIntegral = imageIntegral,
                    n = MAX_BOXES_PER_IMAGE, 
                    font_list = font_list,
                    scale = BOX_SCALE,
                    font_range = FONT_SIZE_RANGE,
                    max_intergral = MAX_INTERGRAL,
                    max_loop = MAX_LOOP)

    if len(boxes_dict) == 0:
        continue
    new_boxes_dict = []
    for box_dict in boxes_dict:
        bbox = box_dict['box']
        x1 = int(bbox[0])
        y1 = int(bbox[1])
        x2 = int(bbox[2])
        y2 = int(bbox[3])
        # box_dict['text_color'] = gen_text_color(np_image[y1:y2, x1:x2], max_diff = 5)
        box_dict['text_color'] = gen_text_color_v2(np_image[y1:y2, x1:x2], min_text_bg_rate = MIN_TEXT_BG_DIFF, max_loop = MAX_LOOP)
        if box_dict['text_color'] is None:
            continue
        else:
            new_boxes_dict.append(box_dict)
    if len(new_boxes_dict) == 0:
        continue

    image_copy = PIL_image.copy()
    points = []
    word_points = []
    for box_dict in new_boxes_dict:
        image_copy = fill_text_to_image(image = image_copy,
                        text = box_dict['text'],
                        font = box_dict['font'],
                        textsize = box_dict['fontsize'],
                        box = box_dict['box'],
                        text_color = box_dict['text_color']
                            )
        box = [int(x) for x in box_dict['box'] ]
        # image_copy = draw_rectangle(image_copy, box[0], box[1], box[2], box[3], line_width = 2)

        points.append([[box[0], box[1]], 
                       [box[2], box[1]], 
                       [box[2], box[3]], 
                       [box[0], box[3]]])
        
        for box in box_dict['word_boxes']:
            box = [int(x) for x in  box]
            word_points.append([[box[0], box[1]], 
                       [box[2], box[1]], 
                       [box[2], box[3]], 
                       [box[0], box[3]]])
    
    shapes = []
    for point in points:
        shapes.append({
            'label' : 'text', 
            'points' : point, 
            'group_id': None,
            'shape_type': 'polygon',
            'flags': {}
        })

    for point in word_points:
        shapes.append({
            'label' : 'word', 
            'points' : point, 
            'group_id': None,
            'shape_type': 'polygon',
            'flags': {}
        })
    
    image_name = f'{sample_id:05d}.jpg'
    image_copy.save(os.path.join(labelme_dir, image_name))
    w, h = image_copy.size
    # # Create an in-memory stream
    # image_stream = io.BytesIO()
    # # Save the PIL image to the in-memory stream in PNG format
    # image_copy.save(image_stream, format='PNG')
    # # Retrieve the encoded image string
    # encoded_string = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    with open(os.path.join(labelme_dir, image_name), "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        

    labelme_data = {
        'version': '5.1.1',
        'flags': {}, 
        'shapes': shapes, 
        'imagePath' : image_name, 
        'imageData': encoded_string,
        'imageHeight': h, 
        'imageWidth': w
    }
    
    json_out = os.path.join(labelme_dir, f'{sample_id:05d}.json')
    with open(json_out, "w") as out:
        json.dump(labelme_data, out)
#     break