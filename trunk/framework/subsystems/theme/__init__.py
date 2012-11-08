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

from google.appengine.ext import ndb

from django.template import TemplateDoesNotExist

from framework.subsystems import cache
from framework.subsystems import utils

CACHE_KEY = 'CUSTOM_THEMES'
DEFAULT_LOCAL_THEME_TEMPLATE = 'Google Code/Default'

class Theme(ndb.Model):

    namespace = ndb.StringProperty()
    body_template_names = ndb.StringProperty(repeated=True)
    body_template_contents = ndb.TextProperty(repeated=True)
    css_filenames = ndb.StringProperty(repeated=True)
    css_contents = ndb.TextProperty(repeated=True)
    js_filenames = ndb.StringProperty(repeated=True)
    js_contents = ndb.TextProperty(repeated=True)
    image_filenames = ndb.StringProperty(repeated=True)
    image_keys = ndb.BlobKeyProperty(repeated=True)

def get_local_theme_namespaces():
    templates = []
    for namespace in os.listdir('./themes'):
        template = []
        for filename in os.listdir('./themes/' + namespace + '/templates'):
            if filename.endswith('.body'):
                template.append([namespace + '/' + filename[:-5], namespace + ' &ndash; ' + filename[:-5]])
        templates.append([namespace, template])
    return templates

def get_custom_theme_namespaces():
    custom_themes = []
    for custom_theme in get_custom_themes():
        templates = []
        for template_name in custom_theme.body_template_names:
            templates.append([custom_theme.namespace + '/' + template_name, custom_theme.namespace + ' &ndash; ' + template_name])
        custom_themes.append([custom_theme.namespace, templates])
    return custom_themes

def is_local_theme_template(t):
    for namespace in os.listdir('./themes'):
        for filename in os.listdir('./themes/' + namespace + '/templates'):
            if namespace + '/' + filename == t + '.body':
                return True
    return False

def is_local_theme_namespace(n):
    return n in os.listdir('./themes')

def get_custom_themes():
    custom_themes = cache.get(CACHE_KEY)
    if not custom_themes:
        custom_themes = Theme.gql("").fetch()
        cache.set(CACHE_KEY, custom_themes)
    return custom_themes

def get_custom_theme(namespace):
    for t in get_custom_themes():
        if t.namespace == namespace:
            return t
    return None

def get_custom_template(theme_template):
    namespace, template_name = theme_template.split('/')
    try:
        t = Theme.query(namespace=namespace).fetch(1)[0]
        index = t.body_template_names.index(template_name)
        return t.body_template_contents[index]
    except:
        pass
    raise TemplateDoesNotExist