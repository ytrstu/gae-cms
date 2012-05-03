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

from framework import content
from framework.subsystems import section
from framework.subsystems import permission
from framework.subsystems import template
from framework.subsystems.theme import DEFAULT_LOCAL_THEME, get_local_themes
from framework.subsystems.forms import form, control, selectcontrol, textareacontrol, checkboxcontrol

class Navigation(content.Content):

    name = 'Navigation'
    author = 'Imran Somji'

    actions = [
        ['create', 'Create', False, False],
        ['edit', 'Edit', False, False],
        ['reorder', 'Reorder', False, False],
        ['delete', 'Delete', False, False],
        ['manage', 'Manage', False, False],
    ]
    views = [
        ['menu', 'Navigation menu', False],
        ['nth_level_only', 'nth level without any children', True],
        ['expanding_hierarchy', 'Entire hierarchy with only the trail to the current section and its children expanded', True],
    ]

    def action_create(self):
        ret = '<h2>Create new section</h2>'
        if self.section.handler.request.get('submit'):
            path, parent_path, name, title, keywords, description, theme, is_private, is_default, redirect_to, new_window = get_values(self.section.handler.request)
            try:
                section.create_section(path, parent_path, name, title, keywords, description, theme, is_private, is_default, redirect_to, new_window)
            except Exception as inst:
                ret += '<div class="status error">%s</div>' %  unicode(inst[0])
            else:
                raise Exception('Redirect', self.section.action_redirect_path)
        ret += get_form(self.section, '', self.section.path)
        return ret

    def action_edit(self):
        ret = '<h2>Edit section "%s"</h2>' % self.section.path
        if self.section.handler.request.get('submit'):
            path, parent_path, name, title, keywords, description, theme, is_private, is_default, redirect_to, new_window = get_values(self.section.handler.request)
            try:
                section.update_section(self.section, path, parent_path, name, title, keywords, description, theme, is_private, is_default, redirect_to, new_window)
            except Exception as inst:
                ret += '<div class="status error">%s</div>' %  unicode(inst[0])
            else:
                raise Exception('Redirect', self.section.action_redirect_path)
        ret += get_form(self.section, self.section.path, self.section.parent_path, self.section.name, self.section.title, self.section.keywords, self.section.description, self.section.theme, self.section.is_private, self.section.is_default, self.section.redirect_to, self.section.new_window)
        return ret

    def action_reorder(self):
        siblings = section.get_siblings(self.section.path)
        if not len(siblings) > 1: raise Exception('BadRequest')
        if self.section.handler.request.get('submit'):
            new_rank = int(self.section.handler.request.get('rank'))
            if self.section.rank != new_rank:
                section.update_section_rank(self.section, new_rank)
            raise Exception('Redirect', self.section.action_redirect_path)
        f = form(self.section, self.section.full_path)
        items = [[0, 'At the top']]
        adder = 1
        for item, _ in siblings:
            if self.section.rank != item['rank']:
                items.append([item['rank'] + adder, 'After ' + item['path']])
            else:
                adder = 0
        f.add_control(selectcontrol(self.section, 'rank', items, self.section.rank, 'Position'))
        f.add_control(control(self.section, 'submit', 'submit'))
        return '<h2>Reorder section "%s"</h2>%s' % (self.section.path, unicode(f))

    def action_delete(self):
        if self.section.handler.request.get('submit'):
            try:
                section.delete_section(self.section)
            except Exception as inst:
                return '<div class="status error">%s</div>' %  unicode(inst[0])
            else:
                raise Exception('Redirect', '/')
        f = form(self.section, self.section.full_path)
        f.add_control(control(self.section, 'submit', 'submit', 'Confirm'))
        return '<div class="status warning">Delete section "%s" and all containing original content?</div>%s' % (self.section.path, unicode(f))

    def action_manage(self):
        ret = '<h2>Manage sections</h2>'
        ret += list_ul(self.section.path, section.get_top_level(), 'manage', True)
        self.section.css.append('nav-manage.css')
        return ret

    def view_nth_level_only(self, params=None):
        n = int(params[0]) if params else 0
        classes = 'nth-level ' + ('horizontal' if not params or len(params) < 2 else params[1])
        hierarchy = section.get_top_level()
        while n:
            for h in hierarchy:
                if section.is_ancestor(self.section.path, h[0]['path']):
                    hierarchy = h[1]
            n -= 1
        parents_only = []
        for item, _ in hierarchy:
            item['is_ancestor'] = section.is_ancestor(self.section.path, item['path'])
            parents_only.append([item, []])
        self.section.css.append('nav-nth-level.css')
        return list_ul(self.section.path, parents_only, classes)

    def view_expanding_hierarchy(self, params=None):
        n = int(params[0]) if params else 0
        classes = 'expanding-hierarchy ' + ('vertical' if not params or len(params) < 2 else params[1])
        hierarchy = section.get_top_level()
        while n:
            for h in hierarchy:
                if section.is_ancestor(self.section.path, h[0]['path']):
                    hierarchy = h[1]
            n -= 1
        for item in hierarchy:
            if(section.is_ancestor(self.section.path, item[0]['path'])):
                item[0]['is_ancestor'] = True
                item[1] = set_ancestry(self.section.path, item[1])
            else:
                item[0]['is_ancestor'] = False
                item[1] = None
        self.section.css.append('nav-expanding-hierarchy.css')
        return list_ul(self.section.path, hierarchy, classes)

    def view_menu(self, params=None):
        return template.snippet('navigation-menu', { 'content': self, 'is_admin': permission.is_admin(self.section.path) })

def get_values(request):
        path = request.get('path').replace('/', '-').replace(' ', '-')
        parent_path = request.get('parent_path').replace('/', '-').replace(' ', '-')
        name = request.get('name')
        title = request.get('title')
        keywords = request.get('keywords')
        description = request.get('description')
        theme = request.get('theme')
        is_private = request.get('is_private') != ''
        is_default = request.get('is_default') != ''
        redirect_to = request.get('redirect_to')
        new_window = request.get('new_window') != ''
        return path, parent_path, name, title, keywords, description, theme, is_private, is_default, redirect_to, new_window

def get_form(s, path, parent_path, name=None, title=None, keywords=None, description=None, theme=None, is_private=False, is_default=False, redirect_to=None, new_window=False):
    f = form(s, s.full_path)
    f.add_control(control(s, 'text', 'path', path, 'Path'))
    f.add_control(control(s, 'text', 'parent_path', parent_path if parent_path else '', 'Parent path'))
    f.add_control(control(s, 'text', 'name', name if name else '', 'Name', 30))
    f.add_control(control(s, 'text', 'title', title if title else '', 'Title', 60))
    f.add_control(textareacontrol(s, 'keywords', keywords if keywords else '', 'Keywords', 60, 5))
    f.add_control(textareacontrol(s, 'description', description if description else '', 'Description', 60, 5))
    local_themes = ['Local', [[x, x] for x in get_local_themes()]]
    f.add_control(selectcontrol(s, 'theme', [local_themes], theme if theme else DEFAULT_LOCAL_THEME, 'Theme'))
    f.add_control(checkboxcontrol(s, 'is_private', is_private, 'Is private'))
    if not is_default: f.add_control(checkboxcontrol(s, 'is_default', is_default, 'Is default'))
    f.add_control(control(s, 'text', 'redirect_to', redirect_to if redirect_to else '', 'Redirect to', 60))
    f.add_control(checkboxcontrol(s, 'new_window', new_window, 'New window'))
    f.add_control(control(s, 'submit', 'submit'))
    return unicode(f)

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
    ret = '<a href="/' + item['path'] + '/navigation/edit" class="edit" title="Edit">Edit</a><a href="/' + item['path'] + '/navigation/create" class="subsection" title="Create subsection">, Create subsection</a>'
    if len(section.get_siblings(item['path'])) > 1:
        ret += '<a href="/' + item['path'] + '/navigation/reorder" class="reorder" title="Reorder">, Reorder</a>'
    else:
        ret += '<span class="reorder-disabled" title="Not reorderable, has no siblings">, Not reorderable</span>'
    if not item['is_default'] and not section.get_children(item['path']):
        ret += '<a href="/' + item['path'] + '/navigation/delete" class="delete" title="Delete">, Delete]</a>'
    else:
        ret += '<span class="delete-disabled" title="Not deletable, either default or has children">, Not deletable]</span>'
    return ret