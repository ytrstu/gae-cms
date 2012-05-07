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
from framework.subsystems.file import File

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

    def on_delete(self):
        for i in range(len(self.theme_namespaces)):
            # This can be done more efficiently via GQL
            theme = self.get_theme(self.theme_namespaces[i])
            cache.delete(CACHE_KEY_PREPEND + self.theme_namespaces[i])
            theme.delete()
            del self.theme_keys[i]
            del self.theme_namespaces[i]
        self.update()

    def action_get(self):
        if not self.section.path_params or len(self.section.path_params) != 3:
            raise Exception('NotFound')
        theme = self.get_theme(self.section.path_params[0])
        resource = self.section.path_params[1]
        filename = self.section.path_params[2]
        if resource == 'css':
            filenames, contents = theme.css_filenames, theme.css_contents
            content_type = 'text/css'
        elif resource == 'js':
            filenames, contents = theme.js_filenames, theme.js_contents
            content_type = 'text/javascript'
        elif resource == 'image':
            pass
        else:
            raise Exception('NotFound')
        try:
            index = filenames.index(filename)
            data = db.Blob(str(contents[index]))
        except:
            raise Exception('NotFound')
        else:
            raise Exception('SendFileBlob', File(filename=filename, content_type=content_type, data=data))

    def action_manage(self):
        themes = [self.get_theme(namespace) for namespace in self.theme_namespaces]
        return template.snippet('themes-manage', { 'content': self, 'themes': themes })

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
        theme = self.get_theme(self.section.path_params[0])
        message = ''
        if self.section.handler.request.get('submit'):
            try:
                _, body_template = get_values(self.section.handler.request)
            except Exception as inst:
                message = '<div class="status error">%s</div>' % inst[0]
            else:
                theme.body_template = body_template
                theme.put()
                self.update()
                cache.delete(CACHE_KEY_PREPEND + str(theme.key()))
                raise Exception('Redirect', self.section.action_redirect_path)
        return '%s<h2>Edit template</h2>%s' % (message, get_form(self.section, theme.namespace, theme.body_template, True))

    def action_delete(self):
        if not self.section.path_params or len(self.section.path_params) != 1:
            raise Exception('NotFound')
        theme = self.get_theme(self.section.path_params[0])
        if self.section.handler.request.get('submit'):
            self.theme_keys.remove(str(theme.key()))
            self.theme_namespaces.remove(theme.namespace)
            cache.delete(CACHE_KEY_PREPEND + str(theme.key()))
            theme.delete()
            self.update()
            raise Exception('Redirect', self.section.action_redirect_path)
        f = form(self.section, self.section.full_path)
        f.add_control(control(self.section, 'submit', 'submit', 'Confirm'))
        return '<div class="status warning">Are you sure you wish to delete theme "%s" and all associated resources?</div>%s' % (theme.namespace, unicode(f))

    def get_theme(self, namespace):
        item = None
        try:
            key = self.theme_keys[self.theme_namespaces.index(namespace)]
            item = cache.get(CACHE_KEY_PREPEND + key)
            if not item:
                item = Theme.get(key)
                cache.set(CACHE_KEY_PREPEND + key, item)
        finally:
            if not item:
                raise Exception('NotFound')
            return item

    def action_edit_css(self):
        if not self.section.path_params or len(self.section.path_params) > 2:
            raise Exception('NotFound')
        theme = self.get_theme(self.section.path_params[0])
        filename = self.section.path_params[1] if len(self.section.path_params) == 2 else ''
        return self.edit_text_resource(theme, filename, theme.css_filenames, theme.css_contents)

    def action_edit_js(self):
        if not self.section.path_params or len(self.section.path_params) > 2:
            raise Exception('NotFound')
        theme = self.get_theme(self.section.path_params[0])
        filename = self.section.path_params[1] if len(self.section.path_params) == 2 else ''
        return self.edit_text_resource(theme, filename, theme.js_filenames, theme.js_contents)

    def edit_text_resource(self, theme, filename, filenames, contents):
        if filename:
            index = filenames.index(filename)
            content = contents[index]
        else:
            index = len(filenames) if filenames else 0
            content = ''
        message = ''
        if self.section.handler.request.get('submit'):
            new_filename = self.section.handler.request.get('filename')
            content = self.section.handler.request.get('content')
            if not new_filename:
                message = '<div class="status error">Filename is required</div>'
            elif filename != new_filename and new_filename in filenames:
                message = '<div class="status error">Filename already exists</div>'
            else:
                if filename:
                    filenames[index] = new_filename
                    contents[index] = db.Text(content)
                else:
                    filenames.append(new_filename)
                    contents.append(db.Text(content))
                theme.put()
                cache.delete(CACHE_KEY_PREPEND + str(theme.key()))
                raise Exception('Redirect', self.section.action_redirect_path)
        f = form(self.section, self.section.full_path)
        f.add_control(control(self.section, 'text', 'filename', filename, 'Filename'))
        f.add_control(textareacontrol(self.section, 'content', content, 'Content', 90, 50))
        f.add_control(control(self.section, 'submit', 'submit', 'Submit'))
        return '%s<h1>Add CSS</h1>%s' % (message, unicode(f))

    def action_delete_css(self):
        if not self.section.path_params or len(self.section.path_params) != 2:
            raise Exception('NotFound')
        theme = self.get_theme(self.section.path_params[0])
        if self.section.path_params[1] not in theme.css_filenames:
            raise Exception('NotFound')
        return self.delete_text_resource(theme, self.section.path_params[1], theme.css_filenames, theme.css_contents)

    def action_delete_js(self):
        if not self.section.path_params or len(self.section.path_params) != 2:
            raise Exception('NotFound')
        theme = self.get_theme(self.section.path_params[0])
        if self.section.path_params[1] not in theme.js_filenames:
            raise Exception('NotFound')
        return self.delete_text_resource(theme, self.section.path_params[1], theme.js_filenames, theme.js_contents)

    def delete_text_resource(self, theme, filename, filenames, contents):
        if self.section.handler.request.get('submit'):
            index = filenames.index(filename)
            del filenames[index]
            del contents[index]
            theme.put()
            cache.delete(CACHE_KEY_PREPEND + str(theme.key()))
            raise Exception('Redirect', self.section.action_redirect_path)
        f = form(self.section, self.section.full_path)
        f.add_control(control(self.section, 'submit', 'submit', 'Confirm'))
        return '<div class="status warning">Are you sure you wish to delete "%s"?</div>%s' % (filename, unicode(f))

    def view_menu(self, params=None):
        return template.snippet('themes-menu', { 'content': self })

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