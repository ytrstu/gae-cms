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

import os, importlib

from google.appengine.ext import db

import framework.content as content
from framework.subsystems import permission
from framework.subsystems.forms import form, control, selectcontrol

class Container(content.Content):

    content_keys = db.StringListProperty()
    content_types = db.StringListProperty()
    content_views = db.StringListProperty()

    name = 'Container'
    author = 'Imran Somji'

    actions = [
        ['add', 'Add content', False],
        ['reorder', 'Reorder', False],
        ['delete', 'Delete', False],
    ]
    views = [
        ['default', 'Default', False],
    ]

    def action_add(self, item):
        if self.section.handler.request.get('submit'):
            rank = int(self.section.p_params[1])
            name, view = self.section.handler.request.get('content_view').split('.')
            # TODO: Ensure that all of the previous actually exist
            m = importlib.import_module('framework.content.' + name)
            for v in getattr(m, name.title())().views:
                if v[0] == view and v[2]:
                    contentmod = getattr(m, name.title())(scope=item.scope, section_path=self.section.path, location_id=item.location_id, rank=rank).init(self)
                    ranked_item = getattr(contentmod, 'get_else_create')(item.scope, self.section.path, item.location_id, rank)
                    item.content_keys.append(str(ranked_item.content_key(item.scope, self.section.path, item.location_id, rank)))
                    item.content_types.append(name)
                    item.content_views.append(view)
                    item.put()
                    break
            raise Exception('Redirect', '/' + (self.section.path if not self.section.is_default else ''))
        content_views = []
        for name in os.listdir('framework/content'):
            if os.path.isdir('framework/content/' + name) and os.path.isfile('framework/content/' + name + '/__init__.py'):
                m = importlib.import_module('framework.content.' + name)
                for v in getattr(m, name.title())().views:
                    if v[2]:
                        content_views.append([name + '.' + v[0], name.title() + ' ----- ' + v[1]])
        f = form(self.section.full_path)
        f.add_control(selectcontrol('content_view', content_views, label='Content - Views'))
        f.add_control(control('submit', 'submit'))
        return '<h2>Add content</h2>%s' % unicode(f)

    def view_default(self, item, params):
        ret = ''
        rank = 0
        add_action = self.actions[0]
        can_add = permission.perform_action(self, self.section.path, self.__class__.__name__.lower(), add_action[0])
        if can_add:
            self.section.css.append('container.css')
            add_link = '<a class="container add" href="/' + self.section.path + '/' + self.__class__.__name__.lower() + '/' + add_action[0] + '/' + self.location_id + '/%d">' + add_action[1] + '</a>'
        for i in range(len(item.content_types)):
            if can_add: ret += add_link % rank
            ret += self.section.get_view(item.scope, item.location_id, item.content_types[i], item.content_views[i], rank=rank, params=None)
            rank += 1
        if can_add: ret += add_link % rank
        return ret