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

from framework.subsystems import permission
from framework.modules.base import import_class

from framework.modules.navigation import navigation

import settings

class Section(db.Model):
    path = db.StringProperty()
    parent_path = db.StringProperty()
    title = db.StringProperty()
    keywords = db.StringProperty()
    description = db.StringProperty()
    rank = db.IntegerProperty()
    is_private = db.BooleanProperty(default=False)
    
    rest_path = None
    
    def __str__(self):
        if not permission.view_section(self): raise Exception('AccessDenied', self.path)
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'theme/templates/Default.html')
        loginout_url = self.path if self.path != settings.DEFAULT_SECTION else '/'
        
        return template.render(path, {
            'user': users.get_current_user(),
            'is_admin': permission.is_admin(path),
            'logout_url': users.create_logout_url(loginout_url),
            'login_url': users.create_login_url(loginout_url),
            'self': self,
            'classes': 'section' + self.path.replace('/', '-').rstrip('-'),
            'action': self.module() if self.rest_path else None,
            'body': self.module() if self.rest_path else '<h2>Under Construction</h2>',
        })
        
    def module(self):
        package = "framework.modules." + self.rest_path.split('/')[0]
        class_name = package.split('.')[-1]
        m = __import__(package, globals(), locals(), [class_name])
        klass = getattr(m, class_name)
        return klass(self.path, self.rest_path).__str__()

def section_key(path):
    return db.Key.from_path('Section', path)

def get_section(base_path, rest_path=None):
    section = Section.gql("WHERE ANCESTOR IS :1 LIMIT 1", section_key(base_path))[0]
    section.rest_path = rest_path
    return section

def create_section(path, parent_path, title):
    section = Section(parent=section_key(path), path=path, parent_path=parent_path, title=title)
    section.put()
    return section