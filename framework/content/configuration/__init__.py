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

from google.appengine.ext import db

from framework import content
from framework.subsystems import cache
from framework.subsystems import template
from framework.subsystems.forms import form, control, textareacontrol

ROBOTS_TXT_CACHE_KEY = 'ROBOTS_TXT_FILE'
FAVICON_ICO_CACHE_KEY = 'FAVICON_ICO_FILE'

class Configuration(content.Content):

    SITE_HEADER = db.StringProperty()
    SITE_SUB_HEADER = db.StringProperty()
    GOOGLE_ANALYTICS_UA = db.StringProperty()
    ROBOTS_TXT = db.TextProperty()

    name = 'Configuration'
    author = 'Imran Somji'

    actions = [
        ['edit', 'Edit', False],
    ]
    views = [
        ['menu', 'Configuration menu', False],
    ]

    def action_edit(self):
        if self.section.handler.request.get('submit'):
            self.SITE_HEADER = self.section.handler.request.get('SITE_HEADER')
            self.SITE_SUB_HEADER = self.section.handler.request.get('SITE_SUB_HEADER')
            self.GOOGLE_ANALYTICS_UA = self.section.handler.request.get('GOOGLE_ANALYTICS_UA')
            self.ROBOTS_TXT = self.section.handler.request.get('ROBOTS_TXT')
            cache.delete(ROBOTS_TXT_CACHE_KEY)
            self.update()
            raise Exception('Redirect', self.section.action_redirect_path)
        f = form(self.section, self.section.full_path)
        f.add_control(control(self.section, 'text', 'SITE_HEADER', self.SITE_HEADER, 'Site header', 50))
        f.add_control(control(self.section, 'text', 'SITE_SUB_HEADER', self.SITE_SUB_HEADER, 'Site sub-header', 50))
        f.add_control(control(self.section, 'text', 'GOOGLE_ANALYTICS_UA', self.GOOGLE_ANALYTICS_UA, 'Google analytics UA'))
        f.add_control(textareacontrol(self.section, 'ROBOTS_TXT', self.ROBOTS_TXT, 'robots.txt', 90, 5))
        f.add_control(control(self.section, 'submit', 'submit', 'Submit'))
        return '<h2>Edit configuration</h2>%s' % unicode(f)

    def view_menu(self, params=None):
        return template.snippet('configuration-menu', { 'content': self })

def get_robots_txt():
    try:
        item = cache.get(ROBOTS_TXT_CACHE_KEY)
        if not item:
            item = Configuration.gql("")[0].ROBOTS_TXT
            if not item: raise Exception('robots.txt not set')
            cache.set(ROBOTS_TXT_CACHE_KEY, item)
        return item
    except:
        return ''

def get_favicon_ico():
    # TODO: Enable admin to set this file via Configuration
    try:
        item = cache.get(FAVICON_ICO_CACHE_KEY)
        if not item:
            item = file('theme/images/favicon.ico', 'r').read()
            cache.set(FAVICON_ICO_CACHE_KEY, item)
        return item
    except:
        raise Exception('NotFound')