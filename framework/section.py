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

import settings

UNALTERABLE_HOME_PATH = 'home'

class Section(db.Model):
    path = db.StringProperty(required=True)
    parent_path = db.StringProperty()
    title = db.StringProperty()
    name = db.StringProperty()
    keywords = db.StringProperty()
    description = db.StringProperty()
    rank = db.IntegerProperty(default = 0)
    is_private = db.BooleanProperty(default=False)
    
    path_parts = None
    handler = None
    
    def __str__(self):
        if not permission.view_section(self): raise Exception('AccessDenied', self.path)
        loginout_url = self.path if self.path != UNALTERABLE_HOME_PATH else '/'
        params = {
            'CONSTANTS': settings.CONSTANTS,
            'user': users.get_current_user(),
            'is_admin': permission.is_admin(self.path),
            'logout_url': users.create_logout_url(loginout_url),
            'login_url': users.create_login_url(loginout_url),
            'self': self,
            'classes': 'section' + self.path.replace('/', '-').rstrip('-'),
            'primary_ancestor': self.get_primary_ancestor(),
            'main': self.content() if self.path_parts[2] else '<h2>Under Construction</h2>Main content goes here',
        }
        return template.html(params)
        
    def content(self):
        package = "framework.content." + self.path_parts[1]
        try:
            m = __import__(package, globals(), locals(), [self.path_parts[1]])
        except:
            raise Exception('Undefined content', self.path_parts[1])
        klass = getattr(m, self.path_parts[1])
        content = klass(self, self.handler, self.path_parts)
        if not permission.perform_action(content, self.path_parts):
            raise Exception('Permission denied', self.path_parts[0], self.path_parts[1])
        return content
    
    def get_primary_ancestor(self):
        ancestor = self
        while ancestor.parent_path:
            ancestor = get_section(self.handler, [ancestor.parent_path])
        return ancestor

def section_key(path):
    return db.Key.from_path('Section', path)

def get_section(handler, path_parts):
    try:
        section = Section.gql("WHERE ANCESTOR IS :1 LIMIT 1", section_key(path_parts[0]))[0]
        section.handler = handler
        section.path_parts = path_parts
        return section
    except:
        if path_parts[0] == UNALTERABLE_HOME_PATH:
            section = create_section(handler, path=path_parts[0], title='GAE-Python-CMS', force=True)
            section.path_parts = [path_parts[0], 'navigation', 'edit']
            return section
        raise Exception('Page not found', path_parts)

def get_first_level(path):
    return Section.gql("WHERE parent_path IN :1", ['', None])

def get_second_level(path):
    section = get_section(None, [path])
    while section.parent_path:
        section = get_section(None, [section.parent_path])
    return Section.gql("WHERE parent_path=:1", section.path)

def is_ancestor(path, another_path):
    while path != another_path:
        try:
            path = get_section(None, [path]).parent_path
        except:
            return False
    return True

def can_path_exist(path, parent_path, old_path=None):
    if not path:
        raise Exception('Path is required')
    elif is_ancestor(path, parent_path):
        raise Exception('Path recursion detected: Path is a descendant')
    elif is_ancestor(parent_path, path):
        raise Exception('Path recursion detected: Path is an ancestor')
    if old_path != path:
        try:
            get_section(None, [path])
        except:
            pass
        else:
            raise Exception('Path already exists')
    if parent_path:
        try:
            get_section(None, [parent_path])
        except:
            raise Exception('Parent path does not exist')
    return True

def create_section(handler, path, parent_path=None, name='', title='', force=False):
    if not force and not can_path_exist(path, parent_path): return None
    section = Section(parent=section_key(path), path=path.lower(), parent_path=parent_path.lower() if parent_path else None, name=name, title=title)
    section.put()
    section.handler = handler
    section.path_parts = [path, parent_path, None, None]
    return section

def update_section(old, path, parent_path, name, title):
    path = path.replace('/', '').replace(' ', '').strip().lower()
    parent_path = parent_path.replace('/', '').replace(' ', '').strip().lower()
    if old.path != path:
        can_path_exist(path, parent_path, old.path)
        for child in Section.gql("WHERE parent_path=:1", old.path):
            child.parent_path = path
            child.put()
        new = Section(parent=section_key(path), path=path.lower(), parent_path=parent_path.lower(), name=name, title=title)
        old.delete()
        new.put()
    elif old.parent_path != parent_path:
        can_path_exist(path, parent_path, old.path)
    old.parent_path = parent_path
    old.name = name
    old.title = title
    old.put()