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

from django.template import TemplateDoesNotExist

from framework.subsystems import cache
from framework.subsystems import utils

CACHE_KEY = 'CUSTOM_THEMES'
DEFAULT_LOCAL_THEME = 'Google Code'

class Theme(db.Model):

    namespace = db.StringProperty()
    body_template_names = db.StringListProperty()
    body_template_contents = db.ListProperty(item_type=db.Text)
    css_filenames = db.StringListProperty()
    css_contents = db.ListProperty(item_type=db.Text)
    js_filenames = db.StringListProperty()
    js_contents = db.ListProperty(item_type=db.Text)

def get_local_themes():
    templates = []
    for namespace in os.listdir('./themes'):
        template = []
        for filename in os.listdir('./themes/' + namespace + '/templates'):
            if filename.endswith('.body'):
                template.append([filename[:-5], filename[:-5]])
        templates.append([namespace, template])
    return templates

def is_local_theme(t):
    for namespace in os.listdir('./themes'):
        for filename in os.listdir('./themes/' + namespace + '/templates'):
            if filename.endswith('.body') and filename[:-5] == t:
                return True
    return False

def get_custom_themes():
    custom_themes = cache.get(CACHE_KEY)
    if not custom_themes:
        custom_themes = Theme.gql("")
        cache.set(CACHE_KEY, custom_themes)
    return custom_themes

def get_custom_template(template_name):
    for t in Theme.gql(""):
        try:
            index = t.body_template_names.index(template_name)
            return t.body_template_contents[index]
        except:
            pass
    raise TemplateDoesNotExist