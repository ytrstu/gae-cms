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

from google.appengine.api import users

from framework.subsystems import template
from framework import content
from framework.subsystems import permission

class User(content.Content):

    name = 'User'
    author = 'Imran Somji'

    views = [
        ['slingbar', 'Slingbar', False],
    ]

    def view_slingbar(self, item, params):
        params = {
                  'section': self.section,
                  'content_type': self.name,
                  'namespace': self.namespace,
                  'can_manage': permission.is_admin(self.section.path),
                  'user': users.get_current_user(),
                  'is_admin': permission.is_admin(self.section.path),
                  }
        return template.snippet('slingbar', params)