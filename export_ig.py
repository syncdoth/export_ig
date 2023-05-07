import glob
import os

import fire
from joblib import Parallel, delayed
from PIL import Image, ImageFilter

NAMED_COLORS = {"white": "FFFFFF", "black": "000000", "gray": "484848"}


def parse_hex_color(hex_color: str):
    if isinstance(hex_color, tuple):
        return hex_color
    if hex_color in NAMED_COLORS:
        return parse_hex_color(NAMED_COLORS[hex_color])

    if hex_color.startswith("#"):
        hex_color = hex_color[1:]

    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])
    if len(hex_color) != 6:
        raise ValueError("Invalid hex color")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def make_shadow(image: Image,
                offset: tuple[int],
                border: int,
                bg_color: str,
                shadow_color: str,
                radius=10):
    """
    image: base image to give a drop shadow
    iterations: number of times to apply the blur filter to the shadow
    offset: offset of the shadow as [x,y]
    bg_color: colour of the background
    shadow_color: colour of the drop shadow
    """

    #Calculate the size of the shadow's image
    full_width = image.size[0] + abs(offset[0]) + border
    full_height = image.size[1] + abs(offset[1]) + border

    # parse colors
    bg_color = parse_hex_color(bg_color)
    shadow_color = parse_hex_color(shadow_color)

    #Create the shadow's image. Match the parent image's mode.
    shadow = Image.new(image.mode, (full_width, full_height), bg_color)

    # Place the shadow, with the required offset
    shadow_left = max(offset[0], 0)  #if <0, push the rest of the image right
    shadow_top = max(offset[1], 0)  #if <0, push the rest of the image down
    #Paste in the constant colour
    shadow.paste(shadow_color,
                 [shadow_left, shadow_top, shadow_left + image.size[0], shadow_top + image.size[1]])

    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=radius))

    # Paste the original image on top of the shadow
    img_left = -min(offset[0], 0)  #if the shadow offset was <0, push right
    img_top = -min(offset[1], 0)  #if the shadow offset was <0, push down
    shadow.paste(image, (img_left, img_top))

    return shadow


def add_padding(image: Image,
                pad: int,
                image_to_paste: Image = None,
                aspect_ratio: tuple[int] = (4, 5),
                bg_color: str = "white"):
    width, height = image.size
    if width > height:
        # landscape
        new_width = width + 2 * pad
        new_height = int(new_width / aspect_ratio[1] * aspect_ratio[0])
        image_pos = (pad, int((new_height - height) / 2))
    elif width < height:
        # portrait
        new_height = height + 2 * pad
        new_width = int(new_height / aspect_ratio[1] * aspect_ratio[0])
        image_pos = (int((new_width - width) / 2), pad)
    else:
        #square
        new_width = width + 2 * pad
        new_height = height + 2 * pad

    color = parse_hex_color(bg_color)

    canvas = Image.new(image.mode, (new_width, new_height), color)

    if image_to_paste is not None:
        canvas.paste(image_to_paste, image_pos)
    else:
        canvas.paste(image, image_pos)

    return canvas


def main(input_path,
         output_folder,
         aspect_ratio="4x5",
         shadow_offset=33,
         pad=100,
         radius=15,
         bg_color="white",
         shadow_color="gray",
         n_jobs=10):
    if os.path.isdir(input_path):
        input_path = os.path.join(input_path, "*")

    files = [f for f in glob.glob(input_path) if not os.path.isdir(f)]
    if len(files) == 0:
        raise ValueError("No files found")

    aspect_ratio = tuple(int(x) for x in aspect_ratio.replace(" ", "").lower().split("x"))
    os.makedirs(output_folder, exist_ok=True)

    def _process_image(input_file_path):
        image = Image.open(input_file_path)
        shadowed = make_shadow(image, (shadow_offset, shadow_offset),
                               shadow_offset,
                               bg_color,
                               shadow_color,
                               radius=radius)
        padded = add_padding(image,
                             pad,
                             image_to_paste=shadowed,
                             aspect_ratio=aspect_ratio,
                             bg_color=bg_color)
        basename = os.path.basename(input_file_path)
        fname, ext = os.path.splitext(basename)
        out_fname = os.path.join(output_folder, fname + "-padded" + ext)
        padded.save(out_fname)

    Parallel(n_jobs=n_jobs)(delayed(_process_image)(fname) for fname in files)


if __name__ == '__main__':
    fire.Fire(main)
