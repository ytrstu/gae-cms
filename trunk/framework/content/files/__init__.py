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

from google.appengine.ext import ndb
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.api import files

from framework import content
from framework.subsystems import template
from framework.subsystems.forms import form, control
from framework.subsystems import cache

CACHE_KEY_PREPEND = 'FILE_'

class Files(content.Content):

    file_keys = ndb.BlobKeyProperty(repeated=True)
    filenames = ndb.StringProperty(repeated=True)

    name = 'Files'
    author = 'Imran Somji'

    actions = [
        ['add', 'Add', False, False],
        ['get', 'Get', False, True],
        ['delete', 'Delete', False, False],
        ['manage', 'Manage', False, False],
    ]
    views = [
        ['menu', 'File menu', False],
    ]

    def on_remove(self):
        for key in self.file_keys:
            cache.delete(CACHE_KEY_PREPEND + str(key))
            BlobInfo.get(key).delete()
        self.update()

    def action_add(self):
        ret = '<h2>Add file</h2>'
        if self.section.handler.request.get('submit'):
            filename = self.section.handler.request.POST['data'].filename.replace(' ', '_')
            if not self.get_file(filename):
                content_type = self.section.handler.request.POST['data'].type
                data = self.section.handler.request.get('data')
                handle = files.blobstore.create(mime_type=content_type, _blobinfo_uploaded_filename=filename)
                with files.open(handle, 'a') as f: f.write(data)
                files.finalize(handle)
                key = files.blobstore.get_blob_key(handle)
                self.file_keys.append(key)
                self.filenames.append(filename)
                self.update()
                raise Exception('Redirect', self.section.action_redirect_path)
            ret += '<div class="status error">A file with the same name already exists for this section</div>'
        f = form(self.section, self.section.full_path)
        f.add_control(control(self.section, 'file', 'data', label='Data'))
        f.add_control(control(self.section, 'submit', 'submit', 'Submit'))
        return ret + unicode(f)

    def action_get(self):
        if not self.section.path_params or len(self.section.path_params) != 1:
            raise Exception('NotFound')
        filename = self.section.path_params[0]
        data = self.get_file(filename)
        if not data:
            raise Exception('NotFound')
        raise Exception('SendFileBlob', data.open().read(), data.content_type)

    def action_delete(self):
        if not self.section.path_params or len(self.section.path_params) != 1:
            raise Exception('NotFound')
        filename = self.section.path_params[0]
        if self.section.handler.request.get('submit'):
            data = self.get_file(filename)
            if not data:
                raise Exception('NotFound')
            index = self.filenames.index(filename)
            cache.delete(CACHE_KEY_PREPEND + str(self.file_keys[index]))
            data.delete()
            del self.file_keys[index]
            del self.filenames[index]
            self.update()
            raise Exception('Redirect', self.section.action_redirect_path)
        f = form(self.section, self.section.full_path)
        f.add_control(control(self.section, 'submit', 'submit', 'Confirm'))
        return '<div class="status warning">Are you sure you wish to delete file "%s" from "%s"?</div>%s' % (filename, self.section.path, unicode(f))

    def action_manage(self):
        return template.snippet('files-manage', { 'content': self })

    def view_menu(self, params=None):
        return template.snippet('files-menu', { 'content': self })

    def get_file(self, filename):
        item = None
        try:
            key = self.file_keys[self.filenames.index(filename)]
            item = cache.get(CACHE_KEY_PREPEND + str(key))
            if not item:
                item = BlobInfo.get(key)
                cache.set(CACHE_KEY_PREPEND + str(key), item)
        finally:
            return item