"""
GAE-Python-CMS: Python-based CMS designed for Google App Engine
Copyright (C) 2012
@author: Imran Somji

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
from framework.subsystems import section
from framework.subsystems.forms import form, control, selectcontrol, textareacontrol, checkboxcontrol

class navigation(base.base):

    content_permissions = {
                           'create': 'Create section',
                           'edit': 'Edit section',
                           'reorder': 'Reorder section',
                           }

    def action_create(self):
        ret = '<h2>Create new section</h2>'
        if self.handler.request.get('submit'):
            path, parent_path, name, title, keywords, description, is_private, is_default = get_values(self.handler.request)
            try:
                section.create_section(self.handler, path, parent_path, name, title, keywords, description, is_private, is_default)
            except Exception as inst:
                ret += '<div class="status error">' + str(inst[0]) + '</div>'
            else:
                raise Exception('Redirect', '/' + (path if not is_default else ''))
        ret += get_form('/'.join(self.path_parts).strip('/'), '', self.section.path)
        return ret

    def action_edit(self):
        ret = '<h2>Edit section "' + self.section.path + '"</h2>'
        if self.handler.request.get('submit'):
            path, parent_path, name, title, keywords, description, is_private, is_default = get_values(self.handler.request)
            try:
                section.update_section(self.section, path, parent_path, name, title, keywords, description, is_private, is_default)
            except Exception as inst:
                ret += '<div class="status error">' + str(inst[0]) + '</div>'
            else:
                raise Exception('Redirect', '/' + (path if not self.section.is_default else ''))
        ret += get_form('/'.join(self.path_parts).strip('/'), self.section.path, self.section.parent_path, self.section.name, self.section.title, self.section.keywords, self.section.description, self.section.is_private, self.section.is_default)
        return ret

    def action_reorder(self):
        siblings = section.get_siblings(self.section.path)
        if not len(siblings) > 1: raise Exception('BadRequest')
        if self.handler.request.get('submit'):
            new_rank = int(self.handler.request.get('rank'))
            if self.section.rank != new_rank:
                section.update_section_rank(self.section, new_rank)
            raise Exception('Redirect', '/' + (self.section.path if not self.section.is_default else ''))
        f = form('/'.join(self.path_parts).strip('/'))
        items = [[0, 'At the top']]
        adder = 1
        for item, _ in siblings:
            if self.section.rank != item['rank']:
                items.append([item['rank'] + adder, 'After ' + item['path']])
            else:
                adder = 0
        f.add_control(selectcontrol('rank', items, self.section.rank, 'Position'))
        f.add_control(control('submit', 'submit'))
        return '<h2>Reorder section "' + self.section.path + '"</h2>' + str(f)

def get_values(request):
        path = request.get('path').replace(' ', '').replace('/', '').lower()
        parent_path = request.get('parent_path').replace(' ', '').replace('/', '').lower()
        name = request.get('name')
        title = request.get('title')
        keywords = request.get('keywords')
        description = request.get('description')
        is_private = request.get('is_private') != ''
        is_default = request.get('is_default') != ''
        return path, parent_path, name, title, keywords, description, is_private, is_default
            
def get_form(action, path, parent_path, name=None, title=None, keywords=None, description=None, is_private=False, is_default=False):
    f = form(action)
    f.add_control(control('text', 'path', path, 'Path'))
    f.add_control(control('text', 'parent_path', parent_path if parent_path else '', 'Parent path'))
    f.add_control(control('text', 'name', name if name else '', 'Name', 30))
    f.add_control(control('text', 'title', title if title else '', 'Title', 60))
    f.add_control(textareacontrol('keywords', keywords if keywords else '', 'Keywords', 60, 5))
    f.add_control(textareacontrol('description', description if description else '', 'Description', 60, 5))
    f.add_control(checkboxcontrol('is_private', is_private, 'Is private'))
    if not is_default: f.add_control(checkboxcontrol('is_default', is_default, 'Is default'))
    f.add_control(control('submit', 'submit'))
    return str(f)

def view_nth_level(s, params):
    n = int(params[0])
    classes = 'nth-level ' + ('vertical' if len(params) < 2 else params[1])
    hierarchy = section.get_top_level()
    while n:
        for h in hierarchy:
            if section.is_ancestor(s.path, h[0]['path']):
                hierarchy = h[1]
        n -= 1
    parents_only = []
    for item, _ in hierarchy:
        item['is_ancestor'] = section.is_ancestor(s.path, item['path'])
        parents_only.append([item, []])
    s.css.append('nth-level')
    return list_ul(s.path, parents_only, classes)

def set_ancestry(path, items):
    for item in items:
        if section.is_ancestor(path, item[0]['path']):
            item[0]['is_ancestor'] = True 
            item[1] = set_ancestry(path, item[1])
        else:
            item[0]['is_ancestor'] = False
            item[1] = None
    return items

def view_expanding_hierarchy(s, params):
    n = int(params[0])
    classes = 'expanding-hierarchy ' + ('vertical' if len(params) < 2 else params[1])
    hierarchy = section.get_top_level()
    while n:
        for h in hierarchy:
            if section.is_ancestor(s.path, h[0]['path']):
                hierarchy = h[1]
        n -= 1
    for item in hierarchy:
        if(section.is_ancestor(s.path, item[0]['path'])):
            item[0]['is_ancestor'] = True
            item[1] = set_ancestry(s.path, item[1])
        else:
            item[0]['is_ancestor'] = False
            item[1] = None
    s.css.append('expanding-hierarchy')
    return list_ul(s.path, hierarchy, classes)

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
        li += '<li' + ((' class="' + classes.strip() + '"') if classes.strip() else '') + '><a href="/' + (item['path'] if not item['is_default'] else '') + '">' + (item['name'] if item['name'] else '-') + '</a>'
        if children:
            li += '<ul>' + list_li(path, children) + '</ul>'
        li += '</li>'
        i += 1
    return li