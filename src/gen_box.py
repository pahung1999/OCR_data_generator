import torch
from torchvision import ops
from PIL import ImageFont
import random
import numpy as np
import cv2


def gen_imgInteval(image_in: np.ndarray):
    """
    Generate the integral image of the input image.

    Args:
        image_in (np.ndarray): The input image as a NumPy array.
    Returns:
        np.ndarray: The integral image.
    Raises:
        ValueError: If the input image format is not supported.
    """

    if len(image_in.shape) == 2:
        image_process = np.asarray(image_in)
    elif image_in.shape[2] == 3:
        image_process = cv2.cvtColor(image_in, cv2.COLOR_RGB2BGR)
    elif image_in.shape[2] == 4:
        image_process = cv2.cvtColor(image_in, cv2.COLOR_RGBA2RGB)
    else:
        raise ValueError("wrong image format")

    src_h, src_w = image_process.shape[:2]
    
    # key_points = self._fast.detect(image_process, None)
    kp_image = cv2.Canny(image_process, 50, 150) // 255
    sum_arr = np.zeros((src_h, src_w), np.float32)
    image_integral = cv2.integral(kp_image, sum_arr, cv2.CV_32FC1)

    return image_integral

    
def get_box_size(text: str,
                font: ImageFont,
                fontsize: int,
                ):

    font_copy = font.font_variant(size=fontsize)
    x1, y1, x2, y2 = font_copy.getbbox(text, stroke_width=0)
    text_width, text_height = x2 - x1, y2 - x1

    return text_width, text_height


def box_gen(image_size,
            imageIntegral: np.ndarray,
            text : str,
            font: ImageFont,
            scale = (0.02, 0.5),
            font_range = (5, 50),
            max_intergral = 20,
            max_loop = 1000):
    """
    Generate a bounding box for the text within the specified image size and constraints.

    Args:
        image_size (tuple): The size of the image as a tuple (width, height).
        imageIntegral (np.ndarray): The integral image.
        text (str): The text to place within the bounding box.
        font (ImageFont): The font to use for the text.
        scale (tuple): The scale range of text box height and image height. Default is (0.02, 0.5).
        font_range (tuple): The font size range. Default is (5, 50).
        max_integral (float): The maximum integral value. Default is 20.
        max_loop (int): The maximum number of loop iterations. Default is 1000.

    Returns:
        dict: The bounding box information as a dictionary with keys 'box', 'text', 'fontsize', 'font'.
              If a suitable box cannot be found, 'box' will be None.

    """

    W, H = image_size
    h_range = (H*scale[0], H*scale[1])
    count_height_loop = 0
    count_intergral_loop = 0
    text = text.strip()
    while True:
        if count_height_loop > max_loop or count_intergral_loop > max_loop:
            return {
                    "box": None,
                    "text": text,
                    "fontsize": fontsize,
                    "font": font
                    } 
            
        # if count_intergral_loop > 10000:
        #     # raise ValueError("Can't find suitable integral") 

        fontsize = random.randint(*font_range)
        font_copy = font.font_variant(size=fontsize)
        x1, y1, x2, y2 = font_copy.getbbox(text, stroke_width=0)
        text_width, text_height = x2 - x1, y2 - x1

        # ROI
        x1 = random.uniform(0, W - text_width)
        y1 = random.uniform(0, H - text_height)
        x2 = min(x1 + text_width, W - 1)
        y2 = min(y1 + text_height, H - 1)
        if x1<0 or y1<0 or x2<0 or y2<0:
            continue
        integral = imageIntegral[int(y2), int(x2)] - imageIntegral[int(y2), int(x1)] - imageIntegral[int(y1), int(x2)] + imageIntegral[int(y1), int(x1)]

        if text_height < h_range[0] or text_height > h_range[1]:
            count_height_loop+=1
            continue
        elif integral > max_intergral:
            count_intergral_loop+=1
            continue
        else:
            break
    
    text_box = [x1, y1, x2, y2]
    words = text.split(" ")
    words_size = [get_box_size(word, font, fontsize) for word in words]
    space_width = get_box_size(" ", font, fontsize)[0]

    word_boxes = []
    last_x = text_box[0]
    for i, word in enumerate(words):
        word_width = words_size[i][0]
        word_box = [last_x-space_width/2, text_box[1], last_x+word_width, text_box[3]]
        word_boxes.append(word_box)
        last_x += word_width + space_width

        # print(word_box)

    return {
        "box": text_box,
        "text": text,
        "words": words,
        "word_boxes": word_boxes,
        "fontsize": fontsize,
        "font": font
    }


def text_gen():
    """
    Generate random text from txt files

    Returns:
        str: The generated random text.

    """
    #Texts load
    texts_path = "./train_trg.txt"
    with open(texts_path,"r",encoding="utf-8") as f:
        text = random.choice(f.readlines()).strip('\n')
        # texts_data = [x.strip('\n') for x in f.readlines()]
    
    return text

def random_multi_boxes(image_size, 
                       imageIntegral: np.ndarray,
                       n: int, 
                       font_list: list, 
                       scale = (0.05, 0.5),
                       font_range = (10, 100),
                       max_intergral = 20,
                       max_loop = 1000):
    """
    Generate random multiple bounding boxes on the image.

    Args:
        image_size (tuple): The size of the image as a tuple (width, height).
        imageIntegral (np.ndarray): The integral image.
        n (int): The number of bounding boxes to generate.
        font_list (list): The list of font objects to use.
        scale (tuple): The scale range of text box height and image height. Default is (0.05, 0.5).
        font_range (tuple): The font size range. Default is (10, 100).
        max_integral (float): The maximum integral value. Default is 20.
        max_loop (int): The maximum number of loop iterations. Default is 1000.

    Returns:
        list: A list of dictionaries containing the bounding box information for each box.
              Each dictionary has keys 'box', 'text', 'fontsize', 'font'.

    """
    #Gen random multi rectangle box on image
    boxes_dict_list = [box_gen(image_size = image_size,
                                imageIntegral = imageIntegral,
                                text = text_gen(),
                                font = random.choice(font_list),
                                scale = scale,
                                font_range = font_range,
                                max_intergral = max_intergral,
                                max_loop = max_loop) for _ in range(n)]

    boxes_dict_list = [x for x in boxes_dict_list if x['box'] is not None]
    if len(boxes_dict_list) < 1:
        return []
    rois = torch.tensor([x["box"] for x in boxes_dict_list])
    scores = torch.randn(rois.shape[0])
    keep = ops.nms(rois, scores, 0)
    # rois = rois[keep].type(torch.long)
    boxes_dict_list = [boxes_dict_list[i] for i in keep.tolist()] 
    return boxes_dict_list

def random_roi(
    image_size,
    scale=(0.05, 0.5),
    ratio=(0.5, 0.83),
):  
    """
    Generate a random rectangular region of interest (ROI) within the specified image size.

    Args:
        image_size (tuple): The size of the image as a tuple (width, height).
        scale (tuple): The scale range for the ROI. Default is (0.05, 0.5).
        ratio (tuple): The aspect ratio range for the ROI. Default is (0.5, 0.83).

    Returns:
        tuple: The ROI coordinates as a tuple (x1, y1, x2, y2).

    """
    #Gen random a rectangle box on image
    # SR
    scale = random.uniform(*scale)
    ratio = random.uniform(*ratio)

    # Template size
    W, H = image_size
    h = H * scale
    w = h * ratio

    # ROI
    x1 = random.uniform(0, W - w)
    y1 = random.uniform(0, H - h)
    x2 = min(x1 + w, W - 1)
    y2 = min(y1 + h, H - 1)
    return x1, y1, x2, y2


def random_multi_roi(size, n, scale, ratio):
    """
    Generate random multiple rectangular regions of interest (ROIs) within the specified image size.

    Args:
        size (tuple): The size of the image as a tuple (width, height).
        n (int): The number of ROIs to generate.
        scale (tuple): The scale range for the ROIs.
        ratio (tuple): The aspect ratio range for the ROIs.

    Returns:
        list: A list of tuples containing the ROI coordinates (x1, y1, x2, y2).

    """
    #Gen random multi rectangle box on image
    
    rois = torch.tensor([random_roi(size, scale, ratio) for _ in range(n)])
    scores = torch.randn(rois.shape[0])
    keep = ops.nms(rois, scores, 0)
    
    rois = rois[keep].type(torch.long)
    return rois.tolist()

