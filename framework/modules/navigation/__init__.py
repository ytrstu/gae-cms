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

class navigation(base.base):
    def action_edit(self):
        if self.handler.request.get('path'):
            path, parent_path, title = get_values(self.handler.request)
            section.update_section(self.section, path, parent_path, title)
            self.handler.redirect('/' + (path if self.section.path != section.UNALTERABLE_HOME_PATH else ''))
        return get_form('/'.join(self.path_parts).strip('/'), self.section.path, self.section.parent_path, self.section.title)
    
    def action_create(self):
        if self.handler.request.get('path'):
            path, parent_path, title = get_values(self.handler.request)
            section.create_section(self.handler, path, parent_path, title)
            self.handler.redirect('/' + (path if path != section.UNALTERABLE_HOME_PATH else ''))
        return get_form('/'.join(self.path_parts).strip('/'), '', self.section.path, '')

def get_values(request):
        path = request.get('path').replace(' ', '').replace('/', '').lower()
        parent_path = request.get('parent_path').replace(' ', '').replace('/', '').lower()
        title = request.get('title')
        return path, parent_path, title
            
def get_form(action, path, parent_path, title):
    form = '<form method="POST" action="/' + action + '">'
    if path == section.UNALTERABLE_HOME_PATH:
        form += '<input type="hidden" name="path" id="path" value="' + path + '">'
    else:
        form += '<label for="path">Path</label><input type="text" name="path" id="path" value="' + path + '">'
    form += '<label for="parent_path">Parent Path</label><input type="text" name="parent_path" id="parent_path" value="' + (parent_path if parent_path else '') + '">'
    form += '<label for="title">Title</label><input type="text" size="60" name="title" id="title" value="' + (title if title else '') + '">'
    form += '<input type="submit"></form>'
    return form

def view_top(path):
    top = section.get_top_levels(path)
    if not top: return ''
    list = '<ul class="module navigation view top">'
    for t in top:
        list += '<li><a href="/' + (t.path if t.path != section.UNALTERABLE_HOME_PATH else '') + '">' + t.title + '</a></li>'
    list += '</ul>' 
    return list

def view_children(path):
    children = section.get_children(path)
    if not children: return ''
    list = '<ul class="module navigation view children">'
    for c in children:
        list += '<li><a href="/' + (c.path if c.path != section.UNALTERABLE_HOME_PATH else '') + '">' + c.title + '</a></li>'
    list += '</ul>' 
    return list