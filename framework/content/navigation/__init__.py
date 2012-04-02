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
    content_permissions = {
                           'edit': 'Edit section',
                           'create': 'Create section',
                           }
    def action_edit(self):
        ret = ''
        if self.handler.request.get('submit'):
            path, parent_path, title = get_values(self.handler.request)
            try:
                section.update_section(self.section, path, parent_path, title)
            except Exception as inst:
                ret += '<div class="status error">' + inst[0] + '</div>'
            else:
                raise Exception('Redirect', '/' + (path if path != section.UNALTERABLE_HOME_PATH else ''))
        ret += get_form('/'.join(self.path_parts).strip('/'), self.section.path, self.section.parent_path, self.section.title)
        return ret
    
    def action_create(self):
        ret = ''
        if self.handler.request.get('submit'):
            path, parent_path, title = get_values(self.handler.request)
            try:
                section.create_section(self.handler, path, parent_path, title)
            except Exception as inst:
                ret += '<div class="status error">' + inst[0] + '</div>'
            else:
                raise Exception('Redirect', '/' + (path if path != section.UNALTERABLE_HOME_PATH else ''))
        ret += get_form('/'.join(self.path_parts).strip('/'), '', self.section.path, '')
        return ret

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
    form += '<input type="submit" name="submit" id="submit"></form>'
    return form

def view_top(path):
    top = section.get_top_levels(path)
    if not top: return ''
    ul = '<ul class="content navigation view top">'
    for t in top:
        ul += '<li><a href="/' + (t.path if t.path != section.UNALTERABLE_HOME_PATH else '') + '">' + t.title + '</a></li>'
    ul += '</ul>' 
    return ul

def view_children(path):
    children = section.get_children(path)
    if not children: return ''
    ul = '<ul class="content navigation view children">'
    for c in children:
        ul += '<li><a href="/' + (c.path if c.path != section.UNALTERABLE_HOME_PATH else '') + '">' + c.title + '</a></li>'
    ul += '</ul>' 
    return ul