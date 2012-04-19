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
from framework.subsystems import cache
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

    def action_add(self):
        ret = '<h2>Add content</h2>'
        content_view = self.section.handler.request.get('content_view') if self.section.handler.request.get('content_view') else ''
        namespace = self.section.handler.request.get('namespace').replace('/', '-').replace(' ', '-').lower() if self.section.handler.request.get('namespace') else ''
        if namespace:
            existing_content = content.get_content(namespace)
            existing_content_type = existing_content.__class__.__name__.lower() if existing_content else None
            # TODO: Ensure that the following actually exist
            rank = int(self.section.path_params[0])
            content_type, view = content_view.split('.')
        if self.section.handler.request.get('submit') and not content_view:
            ret += '<div class="status error">Content is required</div>'
        elif self.section.handler.request.get('submit') and not namespace:
            ret += '<div class="status error">Namespace is required</div>'
        elif self.section.handler.request.get('submit') and existing_content_type:
            if existing_content_type != content_type:
                ret += '<div class="status error">Selected namespace already exists for a different type of content</div>'
            else:
                if existing_content.scope == content.SCOPE_LOCAL and not permission.is_admin(existing_content.section_path):
                    ret += '<div class="status error">Selected namespace already exists for content that you are not permitted to manage</div>'
                elif self.section.handler.request.get('confirm'):
                    self.content_keys.insert(rank, str(existing_content.key()))
                    self.namespaces.insert(rank, namespace)
                    self.content_types.insert(rank, content_type)
                    self.content_views.insert(rank, view)
                    self.update()
                    ret += str(existing_content)
                    raise Exception('Redirect', '/' + (self.section.path if not self.section.is_default else ''))
                else:
                    ret += '<div class="status progress">Selected namespace already exists, continue to add a view to this existing content</div>'
                    f = form(self.section.full_path)
                    f.add_control(control('hidden', 'content_view', content_view))
                    f.add_control(control('hidden', 'namespace', namespace))
                    f.add_control(control('hidden', 'confirm', '1'))
                    f.add_control(control('submit', 'submit', 'Confirm'))
                    ret += unicode(f)
                    return ret
        elif self.section.handler.request.get('submit'):
            m = importlib.import_module('framework.content.' + content_type)
            for v in getattr(m, content_type.title())().views:
                if v[0] == view and v[2]:
                    contentmod = getattr(m, content_type.title())().init(self)
                    getattr(contentmod, 'get_else_create')(self.scope, self.section.path, content_type, namespace, self.namespace)
                    self.content_keys.insert(rank, str(content.content_key(self.scope, self.section.path, content_type, namespace)))
                    self.namespaces.insert(rank, namespace)
                    self.content_types.insert(rank, content_type)
                    self.content_views.insert(rank, view)
                    self.update()
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
        f.add_control(control('submit', 'submit', 'Submit'))
        ret += unicode(f)
        return ret

    def view_default(self, params):
        ret = ''
        add_action = self.actions[0]
        can_add = permission.perform_action(self, self.section.path, add_action[0])
        if can_add:
            self.section.css.append('container.css')
            add_link = '<a class="container add" href="/' + self.section.path + '/' + self.namespace + '/' + add_action[0] + '/%d">' + add_action[1] + '</a>'
        for i in range(len(self.content_types)):
            if can_add: ret += add_link % i
            ret += self.section.get_view(self.scope, self.namespaces[i], self.content_types[i].title(), self.content_views[i], params=None)
        if can_add: ret += add_link % len(self.content_types)
        return ret