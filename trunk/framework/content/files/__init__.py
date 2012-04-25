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
from framework.subsystems.file import File
from framework.subsystems import template
from framework.subsystems.forms import form, control
from framework.subsystems import cache

CACHE_KEY_PREPEND = 'FILE_'

class Files(content.Content):

    filenames = db.StringListProperty()
    keys = db.StringListProperty()

    name = 'Files'
    author = 'Imran Somji'

    actions = [
        ['add', 'Add', False],
        ['get', 'Get', False],
    ]
    views = [
        ['menu', 'File menu', False],
    ]

    def action_add(self):
        ret = '<h2>Add file</h2>'
        if self.section.handler.request.get('submit'):
            filename = self.section.handler.request.POST['data'].filename.replace(' ', '_')
            content_type = self.section.handler.request.POST['data'].type
            data = db.Blob(self.section.handler.request.get('data'))
            if filename not in self.filenames:
                key = File(filename=filename, data=data, content_type=content_type).put()
                self.filenames.append(filename)
                self.keys.append(str(key))
                self.update()
                raise Exception('Redirect', '/' + (self.section.path if not self.section.is_default else ''))
            ret += '<div class="status error">A file with the same name already exists</div>'
        f = form(self.section, self.section.full_path)
        f.add_control(control(self.section, 'file', 'data', label='Data'))
        f.add_control(control(self.section, 'submit', 'submit', 'Submit'))
        return ret + unicode(f)

    def action_get(self):
        if not self.section.path_params or len(self.section.path_params) != 1:
            raise Exception('NotFound')
        filename = self.section.path_params[0]
        data = cache.get(CACHE_KEY_PREPEND + filename)
        if not data:
            i = self.filenames.index(filename)
            if i < 0: raise Exception('NotFound')
            data = File.gql("WHERE filename=:1 LIMIT 1", filename)[0]
            cache.set(CACHE_KEY_PREPEND + filename, data)
        raise Exception('SendFileBlob', data)

    def view_menu(self, params=None):
        return template.snippet('files-menu', { 'content': self })