from dataclasses import dataclass, field

from PIL import Image, ImageFilter

from .color_utils import parse_hex_color


@dataclass
class ShadowPadOptions:
    aspect_ratio: str = field(
        default="4x5", metadata={"help": "Aspect ratio of the output image. Separated by `x`"})
    shadow_offset: int | float = field(
        default=33,
        metadata={
            "help": "Offset of the shadow (in pixels))."
                    "if float, it is a ratio of the longer side of the image instead."
        })
    pad: int | float = field(
        default=100,
        metadata={
            "help": "Padding around the image (in pixels)."
                    "if float, it is a ratio of the longer side of the image instead."
        })
    radius: int = field(default=15, metadata={"help": "Radius of the shadow blur"})
    bg_color: str = field(default="white",
                          metadata={"help": "Background color of the output image"})
    shadow_color: str = field(default="gray", metadata={"help": "Shadow color"})

    def __post_init__(self):
        self.aspect_ratio = tuple(
            int(x) for x in self.aspect_ratio.replace(" ", "").lower().split("x"))


def shadow_pad(args: ShadowPadOptions):

    def _process(image):
        shadowed = make_shadow(image, (args.shadow_offset, args.shadow_offset),
                               args.shadow_offset,
                               args.bg_color,
                               args.shadow_color,
                               radius=args.radius)
        padded = add_padding(image,
                             args.pad,
                             image_to_paste=shadowed,
                             aspect_ratio=args.aspect_ratio,
                             bg_color=args.bg_color)
        return padded

    return _process


def make_shadow(image: Image,
                offset: tuple[int | float],
                border: int | float,
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
    width, height = image.size
    if isinstance(offset[0], float):
        offset = (int(offset[0] * width), int(offset[1] * height))
    if isinstance(border, float):
        border = int(border * max(width, height))
    full_width = width + abs(offset[0]) + border
    full_height = height + abs(offset[1]) + border

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
        if isinstance(pad, float):
            pad = int(pad * width)
        new_width = width + 2 * pad
        new_height = int(new_width / aspect_ratio[1] * aspect_ratio[0])
        image_pos = (pad, int((new_height - height) / 2))
    elif width < height:
        # portrait
        if isinstance(pad, float):
            pad = int(pad * height)
        new_height = height + 2 * pad
        new_width = int(new_height / aspect_ratio[1] * aspect_ratio[0])
        image_pos = (int((new_width - width) / 2), pad)
    else:
        #square
        if isinstance(pad, float):
            pad = int(pad * height)
        new_width = width + 2 * pad
        new_height = height + 2 * pad

    color = parse_hex_color(bg_color)

    canvas = Image.new(image.mode, (new_width, new_height), color)

    if image_to_paste is not None:
        canvas.paste(image_to_paste, image_pos)
    else:
        canvas.paste(image, image_pos)

    return canvas
