from dataclasses import dataclass, field
from functools import lru_cache
import colorsys, json, random

from warpaint import ROOT_DIR
from warpaint.model.settings import Settings


# ↓ COLOUR INSTANCES AT END OF FILE. ↓


PALETTE_FILEPATH = ROOT_DIR.joinpath("palette", "palette.json")
COLOURS_MAP = json.loads(PALETTE_FILEPATH.read_text())

ALIAS_FILEPATH = ROOT_DIR.joinpath("palette", "alias.json")
ALIAS_MAP = json.loads(ALIAS_FILEPATH.read_text())

DEFAULT_SHADE, DEFAULT_SATURATION = 5, 1


@dataclass
class Colour:
    name: str = ""
    alias: str = ""
    description: str = ""
    is_active: bool = True
    shades: list = field(default_factory=list)
    settings: Settings = field(default_factory=Settings)

    def highlight_RGB(self, shade=None, saturation=None):
        shade = shade or int(self.settings["highlight_shade"] or DEFAULT_SHADE)
        saturation = saturation or float(self.settings["highlight_saturation"] or DEFAULT_SATURATION)
        return self._get_colour(shade, saturation)

    def fade_RGB(self, shade=None, saturation=None):
        shade = shade or int(self.settings["fade_shade"] or DEFAULT_SHADE)
        saturation = saturation or float(self.settings["fade_saturation"] or DEFAULT_SATURATION)
        return self._get_colour(shade, saturation)

    # • ───────────────────────────
    # • ──── Utils. ────

    def _get_colour(self, shade, saturation):
        HEX_colour = self.shades[str(shade)]
        RGB_colour = _hex_to_rgb(HEX_colour)

        return _desaturate_colour(*RGB_colour, factor=saturation)

    def data(self):
        return {"alias": self.alias, "description": self.description, "is_active": self.is_active}


# • ───────────────────────────
# • ──── Load/Save. ────


def _load_colours(only_active=False):
    settings = Settings()

    for name, shades in COLOURS_MAP.items():
        alias_data = ALIAS_MAP.get(name, {})

        alias = alias_data.get("alias")
        is_active = alias_data.get("is_active", True)
        description = alias_data.get("description")

        if only_active and not is_active:
            continue

        yield Colour(name=name, shades=shades, alias=alias, description=description, is_active=is_active, settings=settings)


def save_colours():
    colour_data = {colour.name: colour.data() for colour in COLOURS}
    ALIAS_FILEPATH.write_text(json.dumps(colour_data))


# • ───────────────────────────
# • ──── Getters. ────


def get_colours(only_active=False):
    if not only_active:
        return list(COLOURS)

    return [colour for colour in COLOURS if colour.is_active]


def get_random_colour():
    colours = get_colours(only_active=True)
    filtered_colours = [colour for colour in colours if colour.name not in ["white", "black", "gray"]]
    return random.choice(filtered_colours or [MISSING_COLOUR])


def get_colour_by_index(index):
    colours = get_colours(only_active=True)

    if not colours:
        return MISSING_COLOUR

    return colours[index % len(colours)]


# • ───────────────────────────
# • ──── Utils. ────


@lru_cache()
def _hex_to_rgb(hex_colour):
    """Converts a hex colour to an RGB colour.

    Args:
    - hex_colour (str): The hex colour to convert.

    Returns:
    - tuple[int]: The colour as a tuple of red, green, and blue components."""

    hex_colour = hex_colour.lstrip("#")
    return tuple(int(hex_colour[i : i + 2], 16) for i in (0, 2, 4))


@lru_cache()
def _desaturate_colour(red=255, green=255, blue=255, factor=1.0):
    """Desaturates a given RGBA colour by a specified factor. It adjusts the
    saturation of a colour by converting it from RGB to HLS, modifying the saturation,
    and then converting it back to RGB.

    Args:
    - red (int): The red component of the colour, in the range 0-255.
    - green (int): The green component of the colour, in the range 0-255.
    - blue (int): The blue component of the colour, in the range 0-255.
    - factor (float): The factor by which to desaturate the colour, in the range 0-1.

    Returns:
    - list[int]: The desaturated colour as a list of RGB components, each in the
    range 0-255."""

    hue, lightness, saturation = colorsys.rgb_to_hls(*[x / 255.0 for x in [red, green, blue]])

    adjusted_HLS = [hue, lightness, saturation * factor]
    adjusted_RGB = colorsys.hls_to_rgb(*adjusted_HLS)

    return [int(val * 255.0) for val in adjusted_RGB]


COLOURS = list(_load_colours())
MISSING_COLOUR = COLOURS[-1]
