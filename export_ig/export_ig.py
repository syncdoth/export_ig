from dataclasses import dataclass, field
import glob
import os

from joblib import Parallel, delayed
from PIL import Image, ImageFilter
import simple_parsing

from .color_utils import parse_hex_color


def make_shadow(image: Image,
                offset: tuple[int],
                border: int,
                bg_color: str,
                shadow_color: str,
                radius: int = 10):
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


@dataclass
class Options:
    input_path: str = field(metadata={"help": "Path to the image or folder of images to process"})
    output_folder: str = field(metadata={"help": "Path to the output folder"})
    subfoloder: bool = field(
        default=True, metadata={"help": "Whether to create a subfolder in the output folder"})
    aspect_ratio: str = field(
        default="4x5", metadata={"help": "Aspect ratio of the output image. Separated by `x`"})
    shadow_offset: int = field(default=33, metadata={"help": "Offset of the shadow (in pixels))"})
    pad: int = field(default=100, metadata={"help": "Padding around the image (in pixels)"})
    radius: int = field(default=15, metadata={"help": "Radius of the shadow blur"})
    bg_color: str = field(default="white",
                          metadata={"help": "Background color of the output image"})
    shadow_color: str = field(default="gray", metadata={"help": "Shadow color"})
    n_jobs: int = field(default=10, metadata={"help": "Number of jobs to run in parallel"})


def main():
    args = simple_parsing.parse(Options)

    input_path = args.input_path
    if os.path.isdir(args.input_path):
        input_path = os.path.join(input_path, "*")

    files = [f for f in glob.glob(input_path) if not os.path.isdir(f)]
    if len(files) == 0:
        raise ValueError("No files found")

    aspect_ratio = tuple(int(x) for x in args.aspect_ratio.replace(" ", "").lower().split("x"))
    if args.subfoloder:
        output_folder = os.path.join(os.path.dirname(input_path), output_folder)
    os.makedirs(output_folder, exist_ok=True)

    def _process_image(input_file_path):
        image = Image.open(input_file_path)
        shadowed = make_shadow(image, (args.shadow_offset, args.shadow_offset),
                               args.shadow_offset,
                               args.bg_color,
                               args.shadow_color,
                               radius=args.radius)
        padded = add_padding(image,
                             args.pad,
                             image_to_paste=shadowed,
                             aspect_ratio=aspect_ratio,
                             bg_color=args.bg_color)
        basename = os.path.basename(input_file_path)
        fname, ext = os.path.splitext(basename)
        out_fname = os.path.join(output_folder, fname + "-padded" + ext)
        padded.save(out_fname)

    Parallel(n_jobs=args.n_jobs)(delayed(_process_image)(fname) for fname in files)


if __name__ == '__main__':
    main()
