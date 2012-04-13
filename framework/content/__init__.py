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

    name = 'Base Content'
    author = 'Imran Somji'

    actions = [] # Format: [[action_id, action_string, display_in_outer], ...]
    views = [] # Format: [[view_id, view_string, display_in_outer], ...]

    sitewide_singleton = False # Site-wide ontent such as Navigation are not constrained by location_id

    def __unicode__(self):
        location_id = self.section.p_params[0] if self.section.p_params and len(self.section.p_params) > 0 else None
        if not location_id and not self.sitewide_singleton:
            raise Exception('NotFound')
        elif location_id and location_id.endswith('-'):
            raise Exception('NotFound')
        elif location_id and '-' in location_id:
            location_id, rank = location_id.split('-')
        else:
            rank = None
        item = self.get_local_else_global(self.section.path, location_id, rank)
        if not item and not self.sitewide_singleton:
            raise Exception('NotFound')
        return getattr(self, 'action_%s' % self.section.p_action)(item)

    def init(self, section):
        self.section = section
        return self

    def get_local_else_global(self, section_path, location_id, rank):
        if not location_id: return None
        item = self.get(SCOPE_LOCAL, section_path, location_id, rank)
        return item if item else self.get(SCOPE_GLOBAL, section_path, location_id, rank)

    def get_else_create(self, scope, section_path, location_id, rank):
        item = self.get(scope, section_path, location_id, rank)
        if not item:
            self.__init__(parent=self.content_key(scope.upper(), section_path, location_id, rank),
                          scope=scope,
                          section_path=section_path if scope != SCOPE_GLOBAL else None,
                          location_id=location_id, rank=rank)
            self.put()
            item = self
        return item

    def get(self, scope, section_path, location_id, rank):
        if not location_id: raise Exception('location_id is required')
        try:
            return self.gql("WHERE ANCESTOR IS :1 LIMIT 1", self.content_key(scope.upper(), section_path, location_id, rank))[0]
        except:
            return None

    def get_manage_links(self, item):
        allowed = []
        for action in self.actions:
            if action[2] and permission.perform_action(item, self.section.path, self.__class__.__name__.lower(), action[0]):
                allowed.append(action)
        if len(allowed) == 0: return ''

        self.section.css.append('content-permissions.css')
        #self.section.yuijs.append('yui/yui.js')
        #self.section.js.append('content-permissions.js')
        ret = '<ul class="content %s %s permissions"><li><a href="#">%s</a><ul>' % (self.scope.lower(), self.__class__.__name__.lower(), self.name)
        for action in allowed:
            link = '/' + self.section.path + '/' + self.__class__.__name__.lower() + '/' + action[0] + '/' + self.location_id
            ret += '<li><a href="%s">%s</a></li>' % (link, action[1])
        ret += '</ul></li></ul>'
        return ret

    def content_key(self, scope, section_path, location_id, rank):
        path = scope.upper() + '.' + location_id + (('.' + str(rank)) if rank else '')
        if scope.upper() != SCOPE_GLOBAL:
            path = section_path + '.' + path
        return db.Key.from_path(self.__class__.__name__, path)