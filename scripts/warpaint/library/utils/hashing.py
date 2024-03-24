#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import hashlib


def hash_str(content):
    """Computes the MD5 hash of a string."""

    hasher = hashlib.md5()
    hasher.update(content.encode("utf-8"))
    return hasher.hexdigest()
