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
    ancestor = section.get_primary_ancestor(path)[0]
    first_level = section.get_first_level(path)
    first_only = []
    for item, _ in first_level:
        item['is_ancestor'] = item['path'] == ancestor['path']
        first_only.append([item, []])
    return list_ul(path, first_only, "first-level")

def view_second_level(path):
    second_level = section.get_second_level(path)
    for item in second_level:
        item[0]['is_ancestor'] = False
        item[1] = None
    return list_ul(path, second_level, "second-level")

# TODO: Mark ancestors and remove rest for expanding hierarchy
def set_ancestry(path, items):
    for item in items:
        item[0]['is_ancestor'] = False
        item[1] = set_ancestry(path, item[1])
    return items

def view_second_level_expanding_hierarchy(path):
    second_level = set_ancestry(path, section.get_second_level(path))
    return list_ul(path, second_level, "second-level-expanding-hierarchy")

def list_ul(path, items, style):
    if not items: return ''
    ul = '<ul class="content navigation view ' + style + '">'
    ul += list_li(path, items)
    ul += '</ul>' 
    return ul

def list_li(path, items):
    li = ''
    i = 0
    for item, children in items:
        classes = 'current' if item['path'] == path else ''
        if item['is_ancestor']: classes += ' ancestor'
        if not i: classes += ' first '
        li += '<li' + ((' class="' + classes.strip() + '"') if classes.strip() else '') + '><a href="/' + (item['path'] if item['path'] != section.UNALTERABLE_HOME_PATH else '') + '">' + (item['name'] if item['name'] else '-') + '</a>'
        if children:
            li += '<ul>' + list_li(path, children) + '</ul>'
        li += '</li>'
        i += 1
    return li