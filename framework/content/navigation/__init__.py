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
            path, parent_path, name, title = get_values(self.handler.request)
            try:
                section.update_section(self.section, path, parent_path, name, title)
            except Exception as inst:
                ret += '<div class="status error">' + inst[0] + '</div>'
            else:
                raise Exception('Redirect', '/' + (path if path != section.UNALTERABLE_HOME_PATH else ''))
        ret += get_form('/'.join(self.path_parts).strip('/'), self.section.path, self.section.parent_path, self.section.name, self.section.title)
        return ret
    
    def action_create(self):
        ret = ''
        if self.handler.request.get('submit'):
            path, parent_path, name, title = get_values(self.handler.request)
            try:
                section.create_section(self.handler, path, parent_path, name, title)
            except Exception as inst:
                ret += '<div class="status error">' + inst[0] + '</div>'
            else:
                raise Exception('Redirect', '/' + (path if path != section.UNALTERABLE_HOME_PATH else ''))
        ret += get_form('/'.join(self.path_parts).strip('/'), '', self.section.path, '', '')
        return ret

def get_values(request):
        path = request.get('path').replace(' ', '').replace('/', '').lower()
        parent_path = request.get('parent_path').replace(' ', '').replace('/', '').lower()
        name = request.get('name')
        title = request.get('title')
        return path, parent_path, name, title
            
def get_form(action, path, parent_path, name, title):
    form = '<form method="POST" action="/' + action + '">'
    if path == section.UNALTERABLE_HOME_PATH:
        form += '<input type="hidden" name="path" id="path" value="' + path + '">'
    else:
        form += '<label for="path">Path</label><input type="text" name="path" id="path" value="' + path + '">'
    form += '<label for="parent_path">Parent Path</label><input type="text" name="parent_path" id="parent_path" value="' + (parent_path if parent_path else '') + '">'
    form += '<label for="name">Name</label><input type="text" size="60" name="name" id="name" value="' + (name if name else '') + '">'
    form += '<label for="title">Title</label><input type="text" size="60" name="title" id="title" value="' + (title if title else '') + '">'
    form += '<input type="submit" name="submit" id="submit"></form>'
    return form

def view_first_level(path):
    top = section.get_primary_ancestor(path)
    return list_ul(path, section.get_first_level(path), "first-level", top[0]['path'])

def view_second_level(path):
    return list_ul(path, section.get_second_level(path), "second-level")

def list_ul(path, items, style, top_path=None):
    if not items: return ''
    ul = '<ul class="content navigation view ' + style + '">'
    i = 0
    for item, _ in items:
        classes = 'current ' if item['path'] == path or item['path'] == top_path else ''
        if not i: classes += 'first '
        ul += '<li' + ((' class="' + classes.strip() + '"') if classes.strip() else '') + '><a href="/' + (item['path'] if item['path'] != section.UNALTERABLE_HOME_PATH else '') + '">' + (item['name'] if item['name'] else '-') + '</a></li>'
        i += 1
    ul += '</ul>' 
    return ul