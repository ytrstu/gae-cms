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

from framework.subsystems import permission

SCOPE_GLOBAL = 'GLOBAL'
SCOPE_LOCAL = 'LOCAL'

class Content(db.Model):

    scope = db.StringProperty(default=SCOPE_GLOBAL, required=True, choices=[SCOPE_GLOBAL, SCOPE_LOCAL])
    section_path = db.StringProperty(default=None)
    location_id = db.StringProperty()
    rank = db.IntegerProperty(default=None)

    actions = {}
    views = {}

    def __str__(self):
        # If the action doesn't exist, the AttributeError will lead to a 404
        return getattr(self, 'action_%s' % self.section.path_parts[2])()

    def init(self, section):
        self.section = section
        return self

    def get(self, scope, section_path, location_id, rank=None):
        try:
            return self.gql("WHERE scope=:1 AND section_path=:2 AND location_id=:3 AND rank=:4 LIMIT 1", scope, section_path, location_id, rank)[0]
        except:
            return None

    def get_or_create(self, scope, section_path, location_id, rank=None):
        if scope == SCOPE_GLOBAL: section_path = None
        item = self.get(scope, section_path, location_id, rank)
        if not item:
            self.scope=scope
            self.section_path=section_path
            self.location_id=location_id
            self.rank=rank
            self.put()
            item = self
        return item

    def get_manage_links(self, item):
        permissions = []
        for action in self.actions:
            if permission.perform_action(item, [self.section.path, self.__class__.__name__.lower(), action]):
                permissions.append(action)
        if len(permissions) == 0: return ''
        ret = '<ul>'
        for action in permissions:
            ret += '<li><a href="/' + self.section.path + '/' + self.__class__.__name__.lower() + '/' + action + '/' + self.location_id +  '">' + self.actions[action] + '</a></li>'
        ret += '</ul>'
        return ret