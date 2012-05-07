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
        ['delete', 'Delete', False, False],
        ['edit_body_template', 'Edit body template', False, False],
        ['delete_body_template', 'Delete body template', False, False],
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
        message = ''
        if self.section.handler.request.get('submit'):
            namespace = self.section.handler.request.get('namespace')
            if not namespace:
                message = '<div class="status error">Namespace is required</div>'
            elif namespace in self.theme_namespaces:
                message = '<div class="status error">Namespace "%s" already exists</div>' % namespace
            elif namespace in get_local_themes():
                # TODO get_local_theme_namespaces
                message = '<div class="status error">Namespace "%s" is already a local theme</div>' % namespace
            else:
                key = Theme(namespace=namespace).put()
                self.theme_keys.append(str(key))
                self.theme_namespaces.append(namespace)
                self.update()
                raise Exception('Redirect', self.section.action_redirect_path)
        f = form(self.section, self.section.full_path)
        f.add_control(control(self.section, 'text', 'namespace', '', 'Namespace (permanent)'))
        f.add_control(control(self.section, 'submit', 'submit', 'Submit'))
        return '%s<h2>Add theme</h2>%s' % (message, unicode(f))

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

    def action_edit_body_template(self):
        if not self.section.path_params or len(self.section.path_params) > 2:
            raise Exception('NotFound')
        theme = self.get_theme(self.section.path_params[0])
        filename = self.section.path_params[1] if len(self.section.path_params) == 2 else ''
        try:
            ret = self.edit_text_resource(theme, filename, theme.body_template_names, theme.body_template_contents, True)
        except Exception as inst:
            if inst[0] == 'Redirect' and filename != self.section.handler.request.get('filename'):
                pass # TODO: Modify all sections that have the same theme name
                raise Exception(inst[0], inst[1])
        return ret

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

    def edit_text_resource(self, theme, filename, filenames, contents, validate_body_template=False):
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
                try:
                    if validate_body_template:
                        content = validated_body_template(content)
                except Exception as inst:
                    message = '<div class="status error">%s</div>' % inst[0]
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
        return '%s<h1>Add</h1>%s' % (message, unicode(f))

    def action_delete_body_template(self):
        if not self.section.path_params or len(self.section.path_params) != 2:
            raise Exception('NotFound')
        theme = self.get_theme(self.section.path_params[0])
        if self.section.path_params[1] not in theme.body_template_names:
            raise Exception('NotFound')
        return self.delete_text_resource(theme, self.section.path_params[1], theme.body_template_names, theme.body_template_contents)

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

def validated_body_template(body_template):
    if '{{ main|safe }}' not in body_template:
        raise Exception('"{{ main|safe }}" is required in the body template')
    elif '<html>' in body_template or '</html>' in body_template:
        raise Exception('"Body template cannot include &lt;html&gt; tags')
    elif '<body>' in body_template or '</body>' in body_template:
        raise Exception('"Body template cannot include &lt;body&gt; tags')
    return body_template