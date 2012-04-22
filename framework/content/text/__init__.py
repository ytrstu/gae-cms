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

from google.appengine.ext import db

from django.utils.html import strip_tags

from framework import content
from framework.subsystems import template
from framework.subsystems.forms import form, control, textareacontrol

class Text(content.Content):

    titles = db.StringListProperty()
    bodies = db.StringListProperty()

    name = 'Text'
    author = 'Imran Somji'

    actions = [
        ['edit', 'Edit', True],
    ]
    views = [
        ['default', 'Default - multiple items are tabbed', True],
    ]

    def action_edit(self):
        rank = int(self.section.path_params[0]) if self.section.path_params else 0
        if rank > len(self.titles) or rank < 0:
            raise Exception('BadRequest', 'Text item out of range')
        if self.section.handler.request.get('submit'):
            self.titles.insert(rank, self.section.handler.request.get('title'))
            self.bodies.insert(rank, self.section.handler.request.get('body'))
            self.update()
            raise Exception('Redirect', '/' + (self.section.path if not self.section.is_default else ''))
        elif not self.section.path_params and len(self.titles) > 0:
            self.section.css.append('text-edit.css')
            ret = '<h2>Select item</h2>'
            for i in range(len(self.titles)):
                ret += '<div class="text edit item">'
                ret += '<a class="edit item" href="' + self.section.full_path + '/' + str(i) + '">Edit</a>'
                if len(self.titles) > 1:
                    ret += '<a class="reorder item" href="' + self.section.full_path + '/' + str(i) + '">Reorder</a>'
                ret += '<a class="delete item" href="' + self.section.full_path + '/' + str(i) + '">Delete</a>'
                if self.titles[i]: ret += '<h3>' + self.titles[i] + '</h3>'
                ret += self.bodies[i] + '</div>'
            ret += '<a class="add item" href="' + self.section.full_path + '/' + str(len(self.titles)) + '">Add</a>'
            return ret
        title = self.titles[rank] if len(self.titles) > rank else ''
        body = self.bodies[rank] if len(self.bodies) > rank else ''
        ret = '<h2>Edit text</h2>'
        f = form(self.section, self.section.full_path)
        f.add_control(control(self.section, 'text', 'title', title, 'Title', 60))
        f.add_control(textareacontrol(self.section, 'body', body, 'Body', 100, 10, html=True))
        f.add_control(control(self.section, 'submit', 'submit'))
        ret += unicode(f)
        return ret

    def view_default(self, params):
        self.items = []
        for i in range(len(self.titles)):
            self.items.append([self.titles[i], self.bodies[i]])
        return template.snippet('text-default', { 'content': self }) if self.items else ''