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

from .. import base
from ... import section
import settings

class navigation(base.base):
    def str_edit(self):
        if self.handler.request.get('path'):
            path = self.handler.request.get('path').replace(' ', '').replace('/', '').lower()
            parent_path = self.handler.request.get('parent_path').replace(' ', '').replace('/', '').lower()
            title = self.handler.request.get('title')
            new = section.Section(parent=section.section_key(path), path=path, parent_path=parent_path, title=title, rank=self.section.rank)
            section.update_section(self.section, new)
            self.handler.redirect('/' + (new.path if self.section.path != section.HOME_SECTION else ''))
        form = '<form method="POST" action="/' + '/'.join(self.path_parts).strip('/') + '">'
        if self.section.path == section.HOME_SECTION:
            form += '<input type="hidden" name="path" id="path" value="' + self.section.path + '">'
        else:
            form += '<label for="path">Path</label><input type="text" name="path" id="path" value="' + self.section.path + '">'
        form += '<label for="title">Title</label><input type="text" size="60" name="title" id="title" value="' + (self.section.title if self.section.title else '') + '">'
        form += '<label for="parent_path">Parent Path</label><input type="text" name="parent_path" id="parent_path" value="' + (self.section.parent_path if self.section.parent_path else '') + '">'
        form += '<input type="submit"></form>'
        return form