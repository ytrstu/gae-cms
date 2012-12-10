"""
@org: GAE-CMS.COM
@description: Python-based CMS designed for Google App Engine
@(c): gae-cms.com 2012
@author: Imran Somji
@license: GNU GPL v2

This progRAM is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This progRAM is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this progRAM; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import copy, os

from google.appengine.api import memcache

import settings

"""
We wrap memcache to ensure new keys on each deployment and to handle instance caching
"""

CACHE = {}

def get(key):
    key = os.environ['CURRENT_VERSION_ID'] + '_' + key
    if not settings.INSTANCE_CACHING_ENABLED or key not in CACHE:
        val = memcache.Client().get(key)
        CACHE[key] = val
    return CACHE[key]

def set(key, val):
    key = os.environ['CURRENT_VERSION_ID'] + '_' + key
    CACHE[key] = val
    return memcache.Client().set(key, val)

def delete(key):
    key = os.environ['CURRENT_VERSION_ID'] + '_' + key
    del CACHE[key]
    return memcache.Client().delete(key)

def flush_all():
    CACHE.clear()
    return memcache.Client().flush_all()