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

from google.appengine.api import users

def is_admin(path):
    return users.is_current_user_admin() # TODO: currently only super admins can do page management

def view_section(section):
    if not section.is_private:
        return True # TODO: if a parent is private then the child should inherit that
    elif section.is_private and users.is_current_user_admin():
        return True # TODO: currently only super admins can view private page
    return False

def perform_action(content, path_parts):
    if path_parts[2] not in content.actions: raise Exception('NotFound')
    return is_admin(path_parts[0]) # TODO: Check if actually has permission

def view_content(content, section, view):
    if view not in content.views: raise Exception('NotFound')
    return view_section(section)