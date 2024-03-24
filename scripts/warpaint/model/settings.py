#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PySide2 import QtCore  # type: ignore


ORGANISATION, APPLICATION = "BlackSwanEffect", "WarPaint"


class Settings:
    """A wrapper class for QtCore.QSettings to manage application settings This
    class provides a simplified interface for storing, retrieving, and deleting
    settings via item assignment, access, and deletion. A caching layer is implemented
    to reduce the overhead of frequent reads from the underlying storage by keeping
    recently accessed or modified settings in memory.

    Note:
    - Direct modifications to the QSettings outside of this class instance will
    not be reflected in the cache, potentially leading to stale data. It is recommended
    to access and modify settings exclusively through this class.

    - The cache is persistent across instances of this class, meaning that any
    changes made to the settings by one instance will be reflected in the cache
    of another instance."""

    _cache = {}

    def __init__(self, organisation=ORGANISATION, application=APPLICATION):
        self.settings = QtCore.QSettings(organisation, application)

    def __setitem__(self, key, value):
        self.settings.setValue(key, value)
        self._cache[key] = value

    def __getitem__(self, key):
        if key not in self._cache:
            self._cache[key] = self.settings.value(key, None)

        return self._cache[key]

    def __delitem__(self, key):
        self.settings.remove(key)
        self._cache.pop(key, None)

    def clear_cache(self):
        self._cache.clear()
