"""
GAE-Python-CMS: Python-based CMS designed for Google AppEngine
Copyright (C) 2012  Imran Somji

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

from google.appengine.ext import db

class base:
    path = db.StringProperty()
    rank = db.IntegerProperty()
    section_path = db.StringProperty()
    
    base_path = None
    rest_path = None
    action = None
    
    def __init__(self, base_path, rest_path):
        self.base_path = base_path
        self.rest_path = rest_path
        self.action = rest_path.lstrip(self.__class__.__name__).strip('/').split('/')[0]
        
    def __str__(self):
        return self.action
    
def import_class(name):
    mod = __import__(name, fromlist=[name.split('.')[-1]])
    return mod()