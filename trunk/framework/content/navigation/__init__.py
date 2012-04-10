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

    content_actions = {

    'create':   'Create section',
    'edit':     'Edit section',
    'reorder':  'Reorder section',
    'manage':   'Manage sections',

    }

    content_views = {

    'nth_level_only': 'nth level without any children',
    'expanding_hierarchy': 'Entire hierarchy with only the trail to the current section and its children expanded',

    }

    def action_create(self):
        ret = '<h2>Create new section</h2>'
        if self.handler.request.get('submit'):
            path, parent_path, name, title, keywords, description, is_private, is_default, redirect_to, new_window = get_values(self.handler.request)
            try:
                section.create_section(self.handler, path, parent_path, name, title, keywords, description, is_private, is_default, redirect_to, new_window)
            except Exception as inst:
                ret += '<div class="status error">' + str(inst[0]) + '</div>'
            else:
                raise Exception('Redirect', '/' + (path if not is_default else ''))
        ret += get_form('/'.join(self.path_parts).strip('/'), '', self.section.path)
        return ret

    def action_edit(self):
        ret = '<h2>Edit section "' + self.section.path + '"</h2>'
        if self.handler.request.get('submit'):
            path, parent_path, name, title, keywords, description, is_private, is_default, redirect_to, new_window = get_values(self.handler.request)
            try:
                section.update_section(self.section, path, parent_path, name, title, keywords, description, is_private, is_default, redirect_to, new_window)
            except Exception as inst:
                ret += '<div class="status error">' + str(inst[0]) + '</div>'
            else:
                raise Exception('Redirect', '/' + (path if not self.section.is_default else ''))
        ret += get_form('/'.join(self.path_parts).strip('/'), self.section.path, self.section.parent_path, self.section.name, self.section.title, self.section.keywords, self.section.description, self.section.is_private, self.section.is_default, self.section.redirect_to, self.section.new_window)
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

    def action_manage(self):
        ret = '<h2>Manage sections</h2>'
        ret += list_ul(self.section.path, section.get_top_level(), 'manage', True)
        self.section.css.append('nav-manage')
        return ret

def get_values(request):
        path = request.get('path').replace(' ', '').replace('/', '').lower()
        parent_path = request.get('parent_path').replace(' ', '').replace('/', '').lower()
        name = request.get('name')
        title = request.get('title')
        keywords = request.get('keywords')
        description = request.get('description')
        is_private = request.get('is_private') != ''
        is_default = request.get('is_default') != ''
        redirect_to = request.get('redirect_to')
        new_window = request.get('new_window') != ''
        return path, parent_path, name, title, keywords, description, is_private, is_default, redirect_to, new_window
            
def get_form(action, path, parent_path, name=None, title=None, keywords=None, description=None, is_private=False, is_default=False, redirect_to=None, new_window=False):
    f = form(action)
    f.add_control(control('text', 'path', path, 'Path'))
    f.add_control(control('text', 'parent_path', parent_path if parent_path else '', 'Parent path'))
    f.add_control(control('text', 'name', name if name else '', 'Name', 30))
    f.add_control(control('text', 'title', title if title else '', 'Title', 60))
    f.add_control(textareacontrol('keywords', keywords if keywords else '', 'Keywords', 60, 5))
    f.add_control(textareacontrol('description', description if description else '', 'Description', 60, 5))
    f.add_control(checkboxcontrol('is_private', is_private, 'Is private'))
    if not is_default: f.add_control(checkboxcontrol('is_default', is_default, 'Is default'))
    f.add_control(control('text', 'redirect_to', redirect_to if redirect_to else '', 'Redirect to', 60))
    f.add_control(checkboxcontrol('new_window', new_window, 'New window'))
    f.add_control(control('submit', 'submit'))
    return str(f)

def view_nth_level_only(s, scope, location_id, params):
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
    s.css.append('nav-nth-level')
    return list_ul(s.path, parents_only, classes)

def view_expanding_hierarchy(s, scope, location_id, params):
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
    s.css.append('nav-expanding-hierarchy')
    return list_ul(s.path, hierarchy, classes)

def set_ancestry(path, items):
    for item in items:
        if section.is_ancestor(path, item[0]['path']):
            item[0]['is_ancestor'] = True 
            item[1] = set_ancestry(path, item[1])
        else:
            item[0]['is_ancestor'] = False
            item[1] = None
    return items

def list_ul(path, items, style, manage=False):
    if not items: return ''
    ul = '<ul class="content navigation view ' + style + '">'
    ul += list_li(path, items, manage)
    ul += '</ul>' 
    return ul

def list_li(path, items, manage=False):
    li = ''
    i = 0
    for item, children in items:
        classes = 'current' if item['path'] == path else ''
        if 'is_ancestor' in item and item['is_ancestor']: classes += ' ancestor'
        if not i: classes += ' first '
        if item['redirect_to']:
            link = item['redirect_to']
        else:
            link = '/' + (item['path'] if not item['is_default'] else '')
        li += '<li' + ((' class="' + classes.strip() + '"') if classes.strip() else '') + '><a href="' + link + '"' + (' target="_blank"' if item['new_window'] else '') + '>' + (item['name'] if item['name'] else '-') + '</a>'
        if manage: li += get_manage_links(item)
        if children: li += '<ul>' + list_li(path, children, manage) + '</ul>'
        li += '</li>'
        i += 1
    return li

def get_manage_links(item):
    ret = '<a href="/' + item['path'] + '/navigation/edit" class="edit" title="Edit">[Edit</a><a href="/' + item['path'] + '/navigation/create" class="subsection" title="Create subsection">, Create subsection</a>'
    if len(section.get_siblings(item['path'])) > 1:
        ret += '<a href="/' + item['path'] + '/navigation/reorder" class="reorder" title="Reorder">, Reorder]</a>'
    else:
        ret += '<span class="reorder-disabled" title="Not reorderable, has no siblings">, Not reorderable]</a>'
    return ret