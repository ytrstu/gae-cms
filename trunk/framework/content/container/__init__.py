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

from framework import content
from framework.subsystems import permission
from framework.subsystems.forms import form, control, selectcontrol

class Container(content.Content):

    content_keys = db.StringListProperty()
    namespaces = db.StringListProperty()
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
        ret = '<h2>Add content</h2>'
        content_view = self.section.handler.request.get('content_view') if self.section.handler.request.get('content_view') else ''
        namespace = self.section.handler.request.get('namespace').replace('/', '-').replace(' ', '-').lower() if self.section.handler.request.get('namespace') else '' 
        if self.section.handler.request.get('submit') and not self.section.handler.request.get('content_view'):
            ret += '<div class="status error">Content is required</div>'
        elif self.section.handler.request.get('submit') and not self.section.handler.request.get('namespace'):
            ret += '<div class="status error">Container namespace is required</div>'
        elif self.section.handler.request.get('submit') and self.section.handler.request.get('namespace').replace('/', '-').replace(' ', '-').lower() in item.namespaces:
            # TODO: This should actually check section/site wide?
            ret += '<div class="status error">Selected namespace already exists in this container</div>'
        elif self.section.handler.request.get('submit'):
            rank = int(self.section.path_params[0])
            content_type, view = content_view.split('.')
            # TODO: Ensure that all of the previous actually exist
            m = importlib.import_module('framework.content.' + content_type)
            for v in getattr(m, content_type.title())().views:
                if v[0] == view and v[2]:
                    contentmod = getattr(m, content_type.title())().init(self)
                    getattr(contentmod, 'get_else_create')(item.scope, self.section.path, content_type, namespace, self.namespace)
                    item.content_keys.insert(rank, str(content.content_key(item.scope, self.section.path, content_type, namespace)))
                    item.namespaces.insert(rank, namespace)
                    item.content_types.insert(rank, content_type)
                    item.content_views.insert(rank, view)
                    item.put()
                    break
            raise Exception('Redirect', '/' + (self.section.path if not self.section.is_default else ''))
        content_views = [['', '']]
        for content_type in content.get_all_content_types():
            m = importlib.import_module('framework.content.' + content_type)
            views = []
            for v in getattr(m, content_type.title())().views:
                if v[2]:
                    views.append([content_type + '.' + v[0], v[1]])
            if views:
                content_views.append([content_type.title(), views])
        f = form(self.section.full_path)
        f.add_control(selectcontrol('content_view', content_views, content_view, 'Content'))
        f.add_control(control('text', 'namespace', namespace, 'Namespace'))
        f.add_control(control('submit', 'submit'))
        ret += unicode(f)
        return ret

    def view_default(self, item, params):
        ret = ''
        add_action = self.actions[0]
        can_add = permission.perform_action(self, self.section.path, add_action[0])
        if can_add:
            self.section.css.append('container.css')
            add_link = '<a class="container add" href="/' + self.section.path + '/' + self.namespace + '/' + add_action[0] + '/%d">' + add_action[1] + '</a>'
        for i in range(len(item.content_types)):
            if can_add: ret += add_link % i
            ret += self.section.get_view(item.scope, item.namespaces[i], item.content_types[i].title(), item.content_views[i], params=None)
        if can_add: ret += add_link % len(item.content_types)
        return ret