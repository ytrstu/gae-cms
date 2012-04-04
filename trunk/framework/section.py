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
from google.appengine.api import memcache
from google.appengine.api import users

from framework.subsystems import template
from framework.subsystems import permission

import settings

UNALTERABLE_HOME_PATH = 'home'
MEMCACHE_KEY = 'section_hierarchy'

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
            'primary_ancestor': get_primary_ancestor(self.path),
            'main': self.content() if self.path_parts[2] else '<h2>Under Construction</h2>Main content goes here',
        }
        return template.html(params)
        
    def content(self):
        package = "framework.content." + self.path_parts[1]
        try:
            m = __import__(package, globals(), locals(), [self.path_parts[1]])
        except:
            raise Exception('BadRequest', self.path_parts[1])
        klass = getattr(m, self.path_parts[1])
        content = klass(self, self.handler, self.path_parts)
        if not permission.perform_action(content, self.path_parts):
            raise Exception('Forbidden', self.path_parts[0], self.path_parts[1])
        return content

def section_key(path):
    return db.Key.from_path('Section', path)

def get_section(handler, path_parts):
    try:
        section = Section.gql("WHERE ANCESTOR IS :1 LIMIT 1", section_key(path_parts[0]))[0]
        section.handler = handler
        section.path_parts = path_parts
        return section
    except:
        if path_parts[0] == UNALTERABLE_HOME_PATH and not path_parts[1]:
            section = create_section(handler, path=path_parts[0], name='Home', title='GAE-Python-CMS', force=True)
            section.path_parts = [path_parts[0], None, None, None]
            return section
        raise Exception('NotFound', path_parts)

def get_helper(path, hierarchy):
    for item, children in hierarchy:
        if path == item['path']: return item
        val = get_helper(path, children)
        if val: return val
    return None

# TODO: This should replace the get_section function to make it more efficient
def get(path):
    return get_helper(path, cache_get_full_hierarchy())

def get_primary_ancestor_helper(path, hierarchy):
    for item, children in hierarchy:
        if path == item['path'] or get_primary_ancestor_helper(path, children):
            return [item, children]
    return None

def get_primary_ancestor(path):
    return get_primary_ancestor_helper(path, cache_get_full_hierarchy())

def get_first_level(path):
    return cache_get_full_hierarchy()

def get_second_level(path):
    return get_primary_ancestor(path)[1]

def db_get_hierarchy(path=None):
    ret = []
    for s in Section.gql("WHERE parent_path=:1", path):
        ret.append([{'path': s.path, 'parent_path': s.parent_path, 'title': s.title, 'name': s.name, 'keywords': s.keywords, 'description': s.description, 'rank': s.rank, 'is_private': s.is_private}, db_get_hierarchy(s.path)])
    return ret

def cache_get_full_hierarchy():
    hierarchy = memcache.Client().get(MEMCACHE_KEY)
    if hierarchy is not None:
        return hierarchy
    else:
        hierarchy = db_get_hierarchy()
        memcache.Client().set(MEMCACHE_KEY, hierarchy)
        return hierarchy

def is_ancestor(path, another_path):
    while path != another_path:
        section = get(path)
        try:
            path = section['parent_path']
        except:
            return False
    return True

def can_path_exist(path, parent_path, old_path=None):
    if not path:
        raise Exception('Path is required')
    elif parent_path and is_ancestor(path, parent_path):
        raise Exception('Path recursion detected: Path is a descendant')
    elif is_ancestor(parent_path, path):
        raise Exception('Path recursion detected: Path is an ancestor')
    elif old_path != path and get(path):
        raise Exception('Path already exists')
    elif parent_path and not get(parent_path):
        raise Exception('Parent path does not exist')
    return True

def create_section(handler, path, parent_path=None, name='', title='', force=False):
    path = path.replace('/', '').replace(' ', '').strip().lower() if path else None
    parent_path = parent_path.replace('/', '').replace(' ', '').strip().lower() if parent_path else None
    if not force and not can_path_exist(path, parent_path): return None
    section = Section(parent=section_key(path), path=path, parent_path=parent_path, name=name, title=title)
    section.put()
    section.handler = handler
    section.path_parts = [path, parent_path, None, None]
    memcache.Client().delete(MEMCACHE_KEY)
    return section

def update_section(old, path, parent_path, name, title):
    path = path.replace('/', '').replace(' ', '').strip().lower() if path else None
    parent_path = parent_path.replace('/', '').replace(' ', '').strip().lower() if parent_path else None
    if old.path != path:
        can_path_exist(path, parent_path, old.path)
        for child in Section.gql("WHERE parent_path=:1", old.path):
            child.parent_path = path
            child.put()
        new = Section(parent=section_key(path), path=path, parent_path=parent_path, name=name, title=title)
        old.delete()
        new.put()
        return
    elif old.parent_path != parent_path and can_path_exist(path, parent_path, old.path):
        pass # If not can_path_exist it will raise an exception
    old.parent_path = parent_path
    old.name = name
    old.title = title
    old.put()
    memcache.Client().delete(MEMCACHE_KEY)