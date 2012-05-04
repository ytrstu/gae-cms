"""
@org: GAE-CMS.COM
@description: Python-based CMS designed for Google App Engine
@(c): gae-cms.com 2012
@author: Imran Somji
@license: GNU GPL v2

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

from framework.subsystems import cache

CACHE_KEY = 'CUSTOM_THEMES'
DEFAULT_LOCAL_THEME = 'Google Code'

class Theme(db.Model):

    namespace = db.StringProperty()
    body_template = db.TextProperty()
    css_filenames = db.StringListProperty()
    css_contents = db.ListProperty(item_type=db.Text)
    js_filenames = db.StringListProperty()
    js_contents = db.ListProperty(item_type=db.Text)

def get_local_themes():
    templates = []
    directory = os.listdir('theme/templates')
    for filename in directory:
        if filename.endswith('.body'):
            templates.append(filename[:-5])
    return templates

def get_custom_themes():
    custom_themes = cache.get(CACHE_KEY)
    if not custom_themes:
        custom_themes = Theme.gql("")
        cache.set(CACHE_KEY, custom_themes)
    return custom_themes

def get_custom_theme(namespace):
    for t in get_custom_themes():
        if t.namespace == namespace: return t
    return None