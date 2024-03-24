#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class DisableSignals:
    def __init__(self, *objects):
        self.objects = objects

    def __enter__(self):
        for obj in self.objects:
            obj.blockSignals(True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for obj in self.objects:
            obj.blockSignals(False)
