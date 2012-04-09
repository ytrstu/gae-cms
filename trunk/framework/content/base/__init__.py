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

from google.appengine.ext import db

class base:

    path = db.StringProperty()
    rank = db.IntegerProperty()
    section_path = db.StringProperty()

    base_actions = {'administrate': 'Administer permissions'}
    content_actions = {}

    base_views = {}
    content_views = {}

    def all_actions(self):
        self.base_actions.update(self.content_actions)
        return self.base_actions

    def all_views(self):
        self.base_views.update(self.content_views)
        return self.base_views

    def __init__(self, section, handler, path_parts):
        self.section = section
        self.handler = handler
        self.path_parts = path_parts

    def __str__(self):
        # If the action doesn't exist, the AttributeError will lead to a 404
        return getattr(self, 'action_%s' % self.path_parts[2])()