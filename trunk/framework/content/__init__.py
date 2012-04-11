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

    scope = db.StringProperty(choices=[SCOPE_GLOBAL, SCOPE_LOCAL])
    section_path = db.StringProperty(default=None)
    location_id = db.StringProperty()
    rank = db.IntegerProperty(default=None)

    actions = {}
    views = {}

    def __unicode__(self):
        scope = self.section.p_params[0] if self.section.p_params and len(self.section.p_params) > 0 else None
        location_id = self.section.p_params[1] if self.section.p_params and len(self.section.p_params) > 1 else None
        rank = self.section.p_params[2]  if self.section.p_params and len(self.section.p_params) > 2 else None
        # If the action doesn't exist, the AttributeError will lead to a 404
        return getattr(self, 'action_%s' % self.section.p_action)(scope, location_id, rank)

    def init(self, section):
        self.section = section
        return self

    def get(self, scope, section_path, location_id, rank=None):
        if not location_id: raise Exception('location_id is required')
        try:
            return self.gql("WHERE ANCESTOR IS :1 LIMIT 1", self.content_key(scope.upper(), section_path, location_id, rank))[0]
        except:
            return None

    def get_or_create(self, scope, section_path, location_id, rank=None):
        item = self.get(scope, section_path, location_id, rank)
        if not item:
            self.__init__(parent=self.content_key(scope.upper(), section_path, location_id, rank),
                          scope=scope,
                          section_path=section_path if scope != SCOPE_GLOBAL else None,
                          location_id=location_id, rank=rank)
            self.put()
            item = self
        return item

    def get_manage_links(self, item):
        permissions = []
        for action in self.actions:
            if permission.perform_action(item, self.section.path, self.__class__.__name__.lower(), action):
                permissions.append(action)
        if len(permissions) == 0: return ''
        ret = '<ul class="manage-links">'
        for action in permissions:
            ret += '<li><a href="/' + self.section.path + '/' + self.__class__.__name__.lower() + '/' + action + '/' + self.scope.lower() + '/' + self.location_id +  '">' + self.actions[action] + '</a></li>'
        ret += '</ul>'
        return ret

    def content_key(self, scope, section_path, location_id, rank=None):
        path = scope.upper() + '.' + location_id + (('.' + rank) if rank else '')
        if scope.upper() != SCOPE_GLOBAL:
            path = section_path + '.' + path
        return db.Key.from_path(self.__class__.__name__, path)