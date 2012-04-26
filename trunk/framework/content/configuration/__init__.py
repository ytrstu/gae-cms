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
from framework.subsystems import template
from framework.subsystems.forms import form, control

class Configuration(content.Content):

    SITE_HEADER = db.StringProperty()
    SITE_SUB_HEADER = db.StringProperty()
    GOOGLE_ANALYTICS_UA = db.StringProperty()

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
            self.update()
            raise Exception('Redirect', self.action_redirect_path)
        f = form(self.section, self.section.full_path)
        f.add_control(control(self.section, 'text', 'SITE_HEADER', self.SITE_HEADER, 'Site header'))
        f.add_control(control(self.section, 'text', 'SITE_SUB_HEADER', self.SITE_SUB_HEADER, 'Site sub-header'))
        f.add_control(control(self.section, 'text', 'GOOGLE_ANALYTICS_UA', self.GOOGLE_ANALYTICS_UA, 'Google analytics UA'))
        f.add_control(control(self.section, 'submit', 'submit', 'Submit'))
        return '<h2>Edit configuration</h2>%s' % unicode(f)

    def view_menu(self, params=None):
        return template.snippet('configuration-menu', { 'content': self })