"""
@org: GAE-CMS.COM
@description: Python-based CMS designed for Google App Engine
@(c): gae-cms.com 2012
@author: Imran Somji
@license: GNU GPL v2

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

from framework import content
from framework.subsystems.theme import Theme
from framework.subsystems import template
from framework.subsystems.forms import form, control, textareacontrol
from framework.subsystems import cache

CACHE_KEY_PREPEND = 'THEME_'

class Themes(content.Content):

    theme_keys = db.StringListProperty()
    theme_namespaces = db.StringListProperty()

    name = 'Themes'
    author = 'Imran Somji'

    actions = [
        ['add', 'Add', False, False],
        ['edit', 'Edit', False, False],
        ['get', 'Get', False, True],
        ['delete', 'Delete', False, False],
        ['manage', 'Manage', False, False],
    ]
    views = [
        ['menu', 'Theme menu', False],
    ]

    def on_delete(self):
        pass

    def action_add(self):
        if self.section.handler.request.get('submit'):
            message = ''
            try:
                namespace, name, template = get_values(self.section.handler.request)
            except Exception as inst:
                message = inst[0]
            else:
                if not namespace:
                    message = 'Namespace is required'
                elif namespace in self.theme_namespaces:
                    message = 'Namespace "%s" already exists' % namespace
            if message:
                return '<div class="status error">%s</div>%s' % (message, get_form(self.section, namespace, name, template))
            key = Theme(namespace=namespace, name=name, template=template).put()
            self.theme_keys.append(str(key))
            self.theme_namespaces.append(namespace)
            self.update()
            raise Exception('Redirect', self.section.action_redirect_path)
        return '<h2>Add theme</h2>%s' % get_form(self.section)

    def action_edit(self):
        if not self.section.path_params or len(self.section.path_params) != 1:
            raise Exception('NotFound')
        namespace = self.section.path_params[0]
        theme = self.get_theme(namespace)
        if not theme:
            raise Exception('NotFound')
        message = ''
        if self.section.handler.request.get('submit'):
            try:
                _, name, template = get_values(self.section.handler.request)
            except Exception as inst:
                message = '<div class="status error">%s</div>' % inst[0]
            else:
                theme = self.get_theme(namespace)
                theme.name = name
                theme.template = template
                theme.put()
                self.update()
                cache.delete(CACHE_KEY_PREPEND + str(theme.key()))
                raise Exception('Redirect', self.section.action_redirect_path)
        return '%s<h2>Edit theme</h2>%s' % (message, get_form(self.section, theme.namespace, theme.name, theme.template, True))

    def action_get(self):
        pass

    def action_delete(self):
        pass

    def action_manage(self):
        return template.snippet('themes-manage', { 'content': self })

    def view_menu(self, params=None):
        return template.snippet('themes-menu', { 'content': self })

    def get_theme(self, namespace):
        item = None
        try:
            key = self.theme_keys[self.theme_namespaces.index(namespace)]
            item = cache.get(CACHE_KEY_PREPEND + key)
            if not item:
                item = Theme.get(key)
                cache.set(CACHE_KEY_PREPEND + key, item)
        finally:
            return item

def get_values(request):
        namespace = request.get('namespace')
        name = request.get('name')
        template = request.get('template')
        return namespace, name, validated_template(template)

def get_form(s, namespace='', name='', template='', disable_namespace=False):
    f = form(s, s.full_path)
    f.add_control(control(s, 'text', 'namespace', namespace, 'Namespace (permanent)', disabled=disable_namespace))
    f.add_control(control(s, 'text', 'name', name, 'Name', 50))
    f.add_control(textareacontrol(s, 'template', template, 'Template', 90, 50))
    f.add_control(control(s, 'submit', 'submit', 'Submit'))
    return unicode(f)

def validated_template(template):
    if '{{ main|safe }}' not in template:
        raise Exception('"{{ main|safe }}" is required in all templates')
    return db.Text(template)