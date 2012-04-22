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
        if self.section.handler.request.get('submit'):
            i = 0
            self.titles = []
            self.bodies = []
            while self.section.handler.request.get('title' + unicode(i)) or self.section.handler.request.get('body' + unicode(i)):
                title = strip_tags(self.section.handler.request.get('title' + unicode(i))).strip()
                body = self.section.handler.request.get('body' + unicode(i)).strip()
                if title or body:
                    self.titles.append(title)
                    self.bodies.append(body)
                i += 1
            self.update()
            raise Exception('Redirect', '/' + (self.section.path if not self.section.is_default else ''))
        ret = '<h2>Edit text</h2>'
        f = form(self.section, self.section.full_path)
        for i in range(len(self.titles)):
            f.add_control(control(self.section, 'text', 'title' + unicode(i), self.titles[i], 'Title', 60))
            f.add_control(textareacontrol(self.section, 'body' + unicode(i), self.bodies[i], 'Body', 100, 10, html=True))
        f.add_control(control(self.section, 'text', 'title' + unicode(len(self.titles)), '', 'Title', 60))
        f.add_control(textareacontrol(self.section, 'body' + unicode(len(self.bodies)), '', 'Body', 100, 10, html=True))
        f.add_control(control(self.section, 'submit', 'submit'))
        ret += unicode(f)
        return ret

    def view_default(self, params):
        self.items = []
        for i in range(len(self.titles)):
            self.items.append([self.titles[i], self.bodies[i]])
        return template.snippet('text-default', { 'content': self }) if self.items else ''