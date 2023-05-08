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
