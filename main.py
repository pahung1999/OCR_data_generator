import torch
from torchvision import ops
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


def plot_img(img, size=(8, 8)):
    plt.figure(figsize=size)
    plt.imshow(img)
    plt.axis('off')
    plt.show()

#Load font
font_dir = "./data/font/"
font_list =[]
for filename in os.listdir(font_dir):
    font = ImageFont.truetype(os.path.join(font_dir, filename), size=50)
    font_list.append(font)

bg_dir = "./data/background/"


