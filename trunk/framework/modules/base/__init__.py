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
    module_path = None
    action_path = None
    parameter_path = None
    
    def __init__(self, base_path, rest_path):
        self.base_path = base_path
        self.module_path = self.__class__.__name__
        rest_path = rest_path.lstrip(self.module_path).strip('/').split('/')
        self.action_path = rest_path[0]
        self.parameter_path = '/'.join(rest_path[1:]).strip('/')
        
    def __str__(self):
        return getattr(self, 'str_%s' % self.action_path)()
    
    def full_path(self):
        full_path = self.base_path if self.base_path else None
        full_path += ('/' + self.module_path) if self.module_path else ''
        full_path += ('/' + self.action_path) if self.action_path else ''
        full_path += ('/' + self.parameter_path) if self.parameter_path else ''
        return full_path