#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import maya.cmds as cmds
from dataclasses import dataclass, field

from warpaint.library import api
from warpaint.model import colours
from warpaint.model.settings import Settings


@dataclass
class Stroke:
    name: str
    region: str
    polygons: set = field(default_factory=set)
    colour: colours.Colour = field(default_factory=colours.get_random_colour)
    settings: Settings = field(default_factory=Settings)
    is_highlighted: bool = True

    # • ───────────────────────────
    # • ──── Polygons. ────

    def select_polygons(self):
        cmds.select(list(self.polygons))

    def set_polygons(self, polygons):
        self.remove_polygons(self.polygons.copy())
        self.add_polygons(polygons)

    def add_polygons(self, polygons):
        self.polygons.update(polygons)
        self.repaint(polygons)

    def remove_polygons(self, polygons):
        self.polygons.difference_update(polygons)
        api.decolour_polygons(polygons)

    # • ───────────────────────────
    # • ──── Colour. ────

    def repaint(self, polygons=None):
        if self.is_highlighted:
            self.to_highlight(polygons)
        else:
            self.to_fade(polygons)

    def decolourize(self):
        api.decolour_polygons(self.polygons)

    # • ───────────────────────────
    # • ──── Highlight/Fade ────

    def to_highlight(self, polygons=None):
        self.is_highlighted = True
        api.colour_polygons(*self.colour.highlight_RGB(), polygons=polygons or list(self.polygons))

    def to_fade(self, polygons=None):
        self.is_highlighted = False
        api.colour_polygons(*self.colour.fade_RGB(), polygons=polygons or list(self.polygons))

    # • ───────────────────────────
    # • ──── IO. ────

    def data(self):
        indices = [api.get_index(polygon) for polygon in self.polygons]
        return self.name, {"colour_name": self.colour.name, "indices": indices, "region": self.region}
