"""
GAE-Python-CMS: Python-based CMS designed for Google App Engine
Copyright (C) 2012
@author: Imran Somji

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

from framework.subsystems import cache
from framework.subsystems import template
from framework.subsystems import permission

import settings

UNALTERABLE_HOME_PATH = 'home'
CACHE_KEY = 'section_hierarchy'

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
    css = []
    
    def __str__(self):
        if not permission.view_section(self): raise Exception('AccessDenied', self.path)
        loginout_url = self.path if self.path != UNALTERABLE_HOME_PATH else '/'
        params = {
            'CONSTANTS': settings.CONSTANTS,
            'user': users.get_current_user(),
            'is_admin': permission.is_admin(self.path),
            'section_has_siblings': len(get_siblings(self.path)) > 1,
            'logout_url': users.create_logout_url(loginout_url),
            'login_url': users.create_login_url(loginout_url),
            'self': self,
            'classes': 'section' + self.path.replace('/', '-').rstrip('-'),
            'primary_ancestor': get_primary_ancestor(self.path),
            'main': self.content() if self.path_parts[2] else '<h2>Under Construction</h2>Main content goes here',
        }
        return template.html(self, params)
        
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
    return get_helper(path, get_top_level())

def get_primary_ancestor_helper(path, hierarchy):
    for item, children in hierarchy:
        if path == item['path'] or get_primary_ancestor_helper(path, children):
            return [item, children]
    return None

def get_primary_ancestor(path):
    return get_primary_ancestor_helper(path, get_top_level())

def get_second_level(path):
    return get_primary_ancestor(path)[1]

def get_children_helper(path, hierarchy):
    for item, children in hierarchy:
        if path == item['path']: return children
        val = get_children_helper(path, children)
        if val: return val
    return []

def get_children(path):
    if not path: return get_top_level()
    return get_children_helper(path, get_top_level())

def get_siblings(path):
    section = get(path)
    return get_children(section['parent_path']) if section else []

def get_top_level():
    hierarchy = cache.get(CACHE_KEY)
    if hierarchy: return hierarchy
    hierarchy = db_get_hierarchy()
    cache.set(CACHE_KEY, hierarchy)
    return hierarchy

def db_get_hierarchy(path=None):
    ret = []
    for s in Section.gql("WHERE parent_path=:1 ORDER BY rank", path):
        ret.append([{'path': s.path, 'parent_path': s.parent_path, 'rank': s.rank, 'is_private': s.is_private, 'name': s.name, 'title': s.title, 'keywords': s.keywords, 'description': s.description}, db_get_hierarchy(s.path)])
    return ret

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

def create_section(handler, path, parent_path=None, name='', title='', keywords='', description='', force=False):
    path = path.replace('/', '').replace(' ', '').strip().lower() if path else None
    parent_path = parent_path.replace('/', '').replace(' ', '').strip().lower() if parent_path else None
    if not force and not can_path_exist(path, parent_path): return None
    max_rank = 0
    for item, _ in get_children(parent_path):
        if item['rank'] <= max_rank: max_rank = item['rank'] + 1
    section = Section(parent=section_key(path), path=path, parent_path=parent_path, rank=max_rank, name=name, title=title, keywords=keywords, description=description)
    section.put()
    section.handler = handler
    section.path_parts = [path, parent_path, None, None]
    cache.delete(CACHE_KEY)
    return section

def update_section(old, path, parent_path, name, title, keywords, description):
    path = path.replace('/', '').replace(' ', '').strip().lower() if path else None
    parent_path = parent_path.replace('/', '').replace(' ', '').strip().lower() if parent_path else None
    if old.path != path:
        can_path_exist(path, parent_path, old.path)
        for child in Section.gql("WHERE parent_path=:1", old.path):
            child.parent_path = path
            child.put()
        new = Section(parent=section_key(path), path=path, parent_path=parent_path, name=name, title=title, keywords=keywords, description=description)
        old.delete()
        new.put()
        return
    elif old.parent_path != parent_path and can_path_exist(path, parent_path, old.path):
        max_rank = 0
        for item, _ in get_children(parent_path):
            if item['rank'] <= max_rank: max_rank = item['rank'] + 1
        old.rank = max_rank
    old.parent_path = parent_path
    old.name = name
    old.title = title
    old.keywords = keywords
    old.description = description
    old.put()
    cache.delete(CACHE_KEY)

def update_section_rank(section, new_rank):
    larger, smaller = max(section.rank, new_rank), min(section.rank, new_rank)
    for sibling in Section.gql("WHERE parent_path=:1 AND rank>=:2 AND rank<=:3 ORDER BY rank", section.parent_path, smaller, larger):
        if sibling.rank < section.rank:
            sibling.rank += 1
        elif sibling.rank > section.rank:
            sibling.rank -= 1
        else:
            sibling.rank = new_rank
        sibling.put()
    cache.delete(CACHE_KEY)