"""
GAE-Python-CMS: Python-based CMS designed for Google App Engine
Copyright (C) 2012
@author: Imran Somji

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import os

def unique_list(seq, idfun=None):
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result

def file_search(search):
    files = []
    for dirpath, _, filenames in os.walk('.'):
        for filename in filenames:
            if filename in search:
                files.append(os.path.join(dirpath, filename))
    ret = []
    for s in search: # Reorder
        for f in files:
            if f.endswith(os.path.sep + s): ret.append(f)
    return ret

def dir_search(search):
    directories = []
    for dirpath, dirnames, _ in os.walk('.'):
        for dirname in dirnames:
            if dirname in search:
                directories.append(os.path.join(dirpath, dirname))
    ret = []
    for s in search: # Reorder
        for d in directories:
            if d.endswith(os.path.sep + s): ret.append(d)
    return ret