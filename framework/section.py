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
from google.appengine.api import users

from framework.subsystems import template
from framework.subsystems import permission

UNALTERABLE_HOME_PATH = 'home'

class Section(db.Model):
    path = db.StringProperty()
    parent_path = db.StringProperty()
    title = db.StringProperty()
    keywords = db.StringProperty()
    description = db.StringProperty()
    rank = db.IntegerProperty()
    is_private = db.BooleanProperty(default=False)
    
    path_parts = None
    handler = None
    
    def __str__(self):
        if not permission.view_section(self): raise Exception('AccessDenied', self.path)
        loginout_url = self.path if self.path != UNALTERABLE_HOME_PATH else '/'
        params = {
            'user': users.get_current_user(),
            'is_admin': permission.is_admin(self.path),
            'logout_url': users.create_logout_url(loginout_url),
            'login_url': users.create_login_url(loginout_url),
            'self': self,
            'classes': 'section' + self.path.replace('/', '-').rstrip('-'),
            'primary_ancestor': self.get_primary_ancestor(),
            'body': self.module() if self.path_parts[1] else '<h2>Under Construction</h2>',
        }
        return template.html(params)
        
    def module(self):
        package = "framework.modules." + self.path_parts[1]
        m = __import__(package, globals(), locals(), [self.path_parts[1]])
        klass = getattr(m, self.path_parts[1])
        return klass(self, self.handler, self.path_parts)
    
    def get_primary_ancestor(self):
        ancestor = self
        while ancestor.parent_path:
            ancestor = get_section(self.handler, [ancestor.parent_path])
        return ancestor

def section_key(path):
    return db.Key.from_path('Section', path)

def get_section(handler, path_parts):
    section = Section.gql("WHERE ANCESTOR IS :1 LIMIT 1", section_key(path_parts[0]))[0]
    section.handler = handler
    section.path_parts = path_parts
    return section

def get_top_levels(path):
    return Section.gql("WHERE parent_path IN :1", ['', None])

def get_children(path):
    return Section.gql("WHERE parent_path=:1", path)

def create_section(handler, path, parent_path, title):
    # TODO: check that path does not already exist
    section = Section(parent=section_key(path), path=path.lower(), parent_path=parent_path.lower() if parent_path else None, title=title)
    section.put()
    section.handler = handler
    return section

def update_section(old, path, parent_path, title):
    if old.path != path and path != UNALTERABLE_HOME_PATH:
        # TODO: check that new path does not already exist
        new = Section(parent=section_key(path), path=path.lower(), parent_path=parent_path.lower(), title=title)
        old.delete()
        new.put()
    else:
        # TODO: check that parent path exists
        old.parent_path = parent_path.lower()
        old.title = title
        old.put()