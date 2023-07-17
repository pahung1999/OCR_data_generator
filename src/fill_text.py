from PIL import Image, ImageFont, ImageDraw
from typing import Tuple


def fill_text_to_image(image: Image,
                       text: str,
                       font: ImageFont,
                       textsize: int,
                       box: list,
                       text_color: Tuple[int, int, int] = (0, 0, 0),
    ): 
    font_copy=font.font_variant(size=textsize)
    # text_mask = Image.new("RGB", (crop_width, img_height), color = bg_color)
    draw = ImageDraw.Draw(image)
        
    # text_y=abs(img_height-crop_height)
    draw.text((int(box[0]), int(box[1])), text, font=font_copy, fill=text_color)
    
    return image


def draw_rectangle(image, x1, y1, x2, y2, line_width = 2):
    # Create an ImageDraw object
    draw = ImageDraw.Draw(image)

    # Draw the rectangle
    rectangle = [(x1, y1), (x2, y2)]
    draw.rectangle(rectangle, outline='red', width=line_width)

    return image