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

class Text(content.Content):

    items = db.StringListProperty()

    actions = {

    'edit':     'Edit text',

    }

    views = {

    'default': 'Default - multiple items are tabbed',

    }

    def action_edit(self):
        location_id = self.section.p_params[0]
        rank = self.section.p_params[1] if len(self.section.p_params) > 1 else None
        ret = '<h2>Edit text</h2>Coming soon: ' + str(location_id) + '/' + str(rank)
        return ret

    def view_default(self, scope, location_id, params):
        item = self.get_or_create(scope, self.section.path, location_id)
        ret = self.get_manage_links(item)
        ret += '&copy; 2012 GAE-Python-CMS. All Rights Reserved.'.join(item.items)
        return ret