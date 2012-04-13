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
    container_namespaces = db.StringListProperty()
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
        if self.section.handler.request.get('submit') and not self.section.handler.request.get('container_namespace'):
            ret += '<div class="status error">Container namespace is required</div>'
        elif self.section.handler.request.get('submit') and self.section.handler.request.get('container_namespace').replace('/', '-').replace(' ', '-').lower() in item.container_namespaces:
            ret += '<div class="status error">Selected namespace already exists in this container</div>'
        elif self.section.handler.request.get('submit'):
            rank = int(self.section.p_params[1])
            name, view = self.section.handler.request.get('content_view').split('.')
            container_namespace = self.section.handler.request.get('container_namespace').replace('/', '-').replace(' ', '-').lower()
            # TODO: Ensure that all of the previous actually exist
            m = importlib.import_module('framework.content.' + name)
            for v in getattr(m, name.title())().views:
                if v[0] == view and v[2]:
                    contentmod = getattr(m, name.title())(scope=item.scope, section_path=self.section.path, template_namespace=item.template_namespace, container_namespace=container_namespace).init(self)
                    ranked_item = getattr(contentmod, 'get_else_create')(item.scope, self.section.path, item.template_namespace, container_namespace)
                    item.content_keys.insert(rank, str(ranked_item.content_key(item.scope, self.section.path, item.template_namespace, container_namespace)))
                    item.container_namespaces.insert(rank, container_namespace)
                    item.content_types.insert(rank, name)
                    item.content_views.insert(rank, view)
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
        f.add_control(control('text', 'container_namespace', '', 'Container namespace'))
        f.add_control(control('submit', 'submit'))
        ret += unicode(f)
        return ret

    def view_default(self, item, params):
        ret = ''
        add_action = self.actions[0]
        can_add = permission.perform_action(self, self.section.path, self.__class__.__name__.lower(), add_action[0])
        if can_add:
            self.section.css.append('container.css')
            add_link = '<a class="container add" href="/' + self.section.path + '/' + self.__class__.__name__.lower() + '/' + add_action[0] + '/' + self.template_namespace + '/%d">' + add_action[1] + '</a>'
        for i in range(len(item.content_types)):
            if can_add: ret += add_link % i
            ret += self.section.get_view(item.scope, item.template_namespace, item.content_types[i], item.content_views[i], item.container_namespaces[i], params=None)
        if can_add: ret += add_link % len(item.content_types)
        return ret