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
import settings

class navigation(base.base):
    def str_edit(self):
        if self.handler.request.get('path'):
            new_path = self.handler.request.get('path').replace(' ', '').replace('/', '')
            if self.section.path != new_path:
                self.section.path = new_path
                self.section.put()
            self.handler.redirect('/' + (new_path if new_path != settings.DEFAULT_SECTION else ''))
        form = '<form method="POST" action="/' + '/'.join(self.path_parts).strip('/') + '">'
        form += '<label for="path">Path</label><input type="text" class="selected" name="path" id="path" value="' + self.section.path + '">'
        form += '<input type="submit"></form>'
        return form