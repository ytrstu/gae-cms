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

from google.appengine.ext import ndb

from framework import content
from framework.subsystems import cache
from framework.subsystems.file import File
from framework.subsystems import template
from framework.subsystems.theme import DEFAULT_LOCAL_THEME_TEMPLATE, get_local_theme_namespaces, get_custom_theme_namespaces
from framework.subsystems.forms import form, control, checkboxcontrol, selectcontrol, textareacontrol

CACHE_KEY = 'CONFIGURATION'

class Configuration(content.Content):

    SITE_HEADER = ndb.StringProperty()
    SITE_SUB_HEADER = ndb.StringProperty()
    DEFAULT_THEME = ndb.StringProperty()
    GOOGLE_ANALYTICS_UA = ndb.StringProperty()
    ROBOTS_TXT = ndb.TextProperty()
    FAVICON_ICO = ndb.KeyProperty(kind=File)
    ENABLE_THEME_PREVIEW = ndb.BooleanProperty(default=False)
    DEBUG_MODE = ndb.BooleanProperty(default=False)

    name = 'Configuration'
    author = 'Imran Somji'

    actions = [
        ['edit', 'Edit', False, False],
    ]
    views = [
        ['menu', 'Configuration menu', False],
    ]

    def action_edit(self):
        if self.section.handler.request.get('submit'):
            self.SITE_HEADER = self.section.handler.request.get('SITE_HEADER')
            self.SITE_SUB_HEADER = self.section.handler.request.get('SITE_SUB_HEADER')
            self.DEFAULT_THEME = self.section.handler.request.get('DEFAULT_THEME')
            self.GOOGLE_ANALYTICS_UA = self.section.handler.request.get('GOOGLE_ANALYTICS_UA')
            self.ROBOTS_TXT = self.section.handler.request.get('ROBOTS_TXT')
            if self.section.handler.request.get('FAVICON_ICO'):
                data = ndb.BlobProperty(self.section.handler.request.get('FAVICON_ICO'))
                if self.FAVICON_ICO:
                    self.FAVICON_ICO.data = data
                else:
                    self.FAVICON_ICO = File(filename='favicon.ico', content_type='image/x-icon', data=data)
                self.FAVICON_ICO.put()
            self.ENABLE_THEME_PREVIEW = self.section.handler.request.get('ENABLE_THEME_PREVIEW') != ''
            self.DEBUG_MODE = self.section.handler.request.get('DEBUG_MODE') != ''
            cache.delete(CACHE_KEY)
            self.update()
            raise Exception('Redirect', self.section.action_redirect_path)
        f = form(self.section, self.section.full_path)
        f.add_control(control(self.section, 'text', 'SITE_HEADER', self.SITE_HEADER, 'Site header', 50))
        f.add_control(control(self.section, 'text', 'SITE_SUB_HEADER', self.SITE_SUB_HEADER, 'Site sub-header', 50))
        combined_themes = get_local_theme_namespaces() + get_custom_theme_namespaces()
        f.add_control(selectcontrol(self.section, 'DEFAULT_THEME', combined_themes, self.DEFAULT_THEME if self.DEFAULT_THEME else DEFAULT_LOCAL_THEME_TEMPLATE, 'Default theme'))
        f.add_control(control(self.section, 'text', 'GOOGLE_ANALYTICS_UA', self.GOOGLE_ANALYTICS_UA, 'Google analytics UA'))
        f.add_control(control(self.section, 'file', 'FAVICON_ICO', label='favicon.ico'))
        f.add_control(textareacontrol(self.section, 'ROBOTS_TXT', self.ROBOTS_TXT, 'robots.txt', 90, 5))
        f.add_control(checkboxcontrol(self.section, 'ENABLE_THEME_PREVIEW', self.ENABLE_THEME_PREVIEW, 'Enable theme preview'))
        f.add_control(checkboxcontrol(self.section, 'DEBUG_MODE', self.DEBUG_MODE, 'Debug mode'))
        f.add_control(control(self.section, 'submit', 'submit', 'Submit'))
        return '<h2>Edit configuration</h2>%s' % unicode(f)

    def view_menu(self, params=None):
        return template.snippet('configuration-menu', { 'content': self })