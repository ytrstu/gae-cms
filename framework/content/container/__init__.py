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

import framework.content as content
from framework.subsystems import permission

class Container(content.Content):

    location_ids = db.StringListProperty()

    name = 'Container'
    author = 'Imran Somji'

    actions = [
        ['add', 'Add content', False],
        ['reorder', 'Reorder', False],
        ['delete', 'Delete', False],
    ]
    views = [
        ['default', 'Default', False],
    ]

    def action_add(self, item):
        return 'TODO: Add content to container ' + self.section.p_params[0] + ', rank: ' + self.section.p_params[1]

    def view_default(self, item, params):
        ret = ''
        rank = 0
        add_action = self.actions[0]
        can_add = permission.perform_action(self, self.section.path, self.__class__.__name__.lower(), add_action[0])
        if can_add:
            self.section.css.append('container.css')
            add_link = '<a class="container add" href="/' + self.section.path + '/' + self.__class__.__name__.lower() + '/' + add_action[0] + '/' + self.location_id + '/%d">' + add_action[1] + '</a>'
        for cl in self.location_ids:
            if can_add: ret += add_link % rank
            rank += 1
            pass # Need to show module views for those defined
        if can_add: ret += add_link % rank
        return ret