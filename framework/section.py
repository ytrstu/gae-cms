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

import os

from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users

from framework.subsystems import permissions

class Section(db.Model):
    path = db.StringProperty()
    parent_path = db.StringProperty()
    title = db.StringProperty()
    keywords = db.StringProperty()
    description = db.StringProperty()
    
    def __str__(self):
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'theme/templates/Default.html')
        return template.render(path, {
            'user': users.get_current_user(),
            'is_admin': permissions.is_admin(path),
            'logout_url': users.create_logout_url(self.path),
            'login_url': users.create_login_url(self.path),
            'title': self.title,
            'keywords': self.keywords,
            'description': self.description,
            'classes': self.path.replace('/', ' ').strip(),
            'body': '<h2>Under Construction</h2>',
        })

def section_key(path):
    return db.Key.from_path('Section', path)

def get_section(path):
    return Section.gql("WHERE ANCESTOR IS :1 LIMIT 1", section_key(path))[0]

def create_section(path, parent_path, title):
    section = Section(parent=section_key(path), path=path, parent_path=parent_path, title=title)
    section.put()
    return section