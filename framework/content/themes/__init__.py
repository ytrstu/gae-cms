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
from framework.subsystems.theme import Theme, get_local_themes
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
        ['get', 'Get', False, True],
        ['manage', 'Manage', False, False],
        ['add', 'Add', False, False],
        ['edit', 'Edit', False, False],
        ['delete', 'Delete', False, False],
        ['edit_css', 'Edit CSS', False, False],
        ['delete_css', 'Delete CSS', False, False],
        ['edit_js', 'Edit JS', False, False],
        ['delete_js', 'Delete JS', False, False],
        ['add_image', 'Add image', False, False],
        ['delete_image', 'Delete CSS', False, False],
    ]
    views = [
        ['menu', 'Theme menu', False],
    ]

    def action_get(self):
        pass

    def action_manage(self):
        return template.snippet('themes-manage', { 'content': self })

    def on_delete(self):
        for i in range(len(self.theme_namespaces)):
            # This can be done more efficiently via GQL
            theme = self.get_theme(self.theme_namespaces[i])
            cache.delete(CACHE_KEY_PREPEND + self.theme_namespaces[i])
            theme.delete()
            del self.theme_keys[i]
            del self.theme_namespaces[i]
        self.update()

    def action_add(self):
        if self.section.handler.request.get('submit'):
            message = ''
            try:
                namespace, body_template = get_values(self.section.handler.request)
            except Exception as inst:
                message = inst[0]
                namespace = self.section.handler.request.get('namespace')
                body_template = self.section.handler.request.get('body_template')
            else:
                if not namespace:
                    message = 'Name is required'
                elif namespace in self.theme_namespaces:
                    message = 'Name "%s" already exists' % namespace
                elif namespace in get_local_themes():
                    message = 'Name "%s" is already a local theme' % namespace
            if message:
                return '<div class="status error">%s</div>%s' % (message, get_form(self.section, namespace, body_template))
            key = Theme(namespace=namespace, body_template=body_template).put()
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
                _, body_template = get_values(self.section.handler.request)
            except Exception as inst:
                message = '<div class="status error">%s</div>' % inst[0]
            else:
                theme = self.get_theme(namespace)
                theme.body_template = body_template
                theme.put()
                self.update()
                cache.delete(CACHE_KEY_PREPEND + str(theme.key()))
                raise Exception('Redirect', self.section.action_redirect_path)
        return '%s<h2>Edit template</h2>%s' % (message, get_form(self.section, theme.namespace, theme.body_template, True))

    def action_delete(self):
        if not self.section.path_params or len(self.section.path_params) != 1:
            raise Exception('NotFound')
        theme_namespace = self.section.path_params[0]
        if theme_namespace not in self.theme_namespaces:
            raise Exception('NotFound')
        elif self.section.handler.request.get('submit'):
            theme = self.get_theme(theme_namespace)
            if not theme:
                raise Exception('NotFound')
            index = self.theme_namespaces.index(theme_namespace)
            cache.delete(CACHE_KEY_PREPEND + self.theme_keys[index])
            theme.delete()
            del self.theme_keys[index]
            del self.theme_namespaces[index]
            self.update()
            raise Exception('Redirect', self.section.action_redirect_path)
        f = form(self.section, self.section.full_path)
        f.add_control(control(self.section, 'submit', 'submit', 'Confirm'))
        return '<div class="status warning">Are you sure you wish to delete theme "%s" and all associated resources?</div>%s' % (theme_namespace, unicode(f))

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

    def action_edit_css(self):
        if not self.section.path_params or len(self.section.path_params) > 2:
            raise Exception('NotFound')
        theme = self.get_theme(self.section.path_params[0])
        if not theme:
            raise Exception('NotFound')
        filename = self.section.path_params[1] if len(self.section.path_params) == 2 else ''
        if filename:
            index = theme.css_filenames.index(filename)
            css_content = theme.css_contents[index]
        else:
            index = len(theme.css_filenames) if theme.css_filenames else 0
            css_content = ''
        message = ''
        if self.section.handler.request.get('submit'):
            new_filename = self.section.handler.request.get('filename')
            css_content = self.section.handler.request.get('css_content')
            if not new_filename:
                message = '<div class="status error">Filename is required</div>'
            elif filename != new_filename and new_filename in theme.css_filenames:
                message = '<div class="status error">Filename already exists</div>'
            else:
                theme.css_filenames.insert(index, new_filename)
                theme.css_contents.insert(index, db.Text(css_content))
                theme.put()
                cache.delete(CACHE_KEY_PREPEND + str(theme.key()))
                raise Exception('Redirect', self.section.action_redirect_path)
        f = form(self.section, self.section.full_path)
        f.add_control(control(self.section, 'text', 'filename', filename, 'Filename'))
        f.add_control(textareacontrol(self.section, 'css_content', css_content, 'CSS', 90, 50))
        f.add_control(control(self.section, 'submit', 'submit', 'Submit'))
        return '%s<h1>Add CSS</h1>%s' % (message, unicode(f))

def get_values(request):
        namespace = request.get('namespace')
        body_template = request.get('body_template')
        return namespace, validated_body_template(body_template)

def get_form(s, namespace='', body_template='', disable_namespace=False):
    f = form(s, s.full_path)
    f.add_control(control(s, 'text', 'namespace', namespace, 'Name (permanent)', disabled=disable_namespace))
    f.add_control(textareacontrol(s, 'body_template', body_template, 'Body template', 90, 50))
    f.add_control(control(s, 'submit', 'submit', 'Submit'))
    return unicode(f)

def validated_body_template(body_template):
    if '{{ main|safe }}' not in body_template:
        raise Exception('"{{ main|safe }}" is required in the body template')
    elif '<html>' in body_template or '</html>' in body_template:
        raise Exception('"Body template cannot include &lt;html&gt; tags')
    elif '<body>' in body_template or '</body>' in body_template:
        raise Exception('"Body template cannot include &lt;body&gt; tags')
    return body_template