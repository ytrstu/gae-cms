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
GNU General Public License for more detailsection.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import os

from google.appengine.api import users

from framework.subsystems import permission
from framework.subsystems import utils

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.template.loaders.filesystem import Loader
from django.template.loader import render_to_string

def html(section, main=''):
    params = {
        'VERSION': os.environ['CURRENT_VERSION_ID'],
        'user': users.get_current_user(),
        'is_admin': permission.is_admin(section.path),
        'section': section,
        'main': main,
    }

    html = render_to_string('outer.html', params)
    body = render_to_string('default-body.snip', params).strip()
    html = html.replace('<body></body>',
                        '<body class="%s">%s</body>' % (' '.join(section.classes), body),
                        1)

    section.css = section.css + section.themecss
    section.js = section.js + section.themejs

    section.yuicss, section.css, section.yuijs, section.js = (utils.unique_list(x) for x in [section.yuicss, section.css, section.yuijs, section.js])

    section.yuicss = '__'.join([x[:-4] if x.endswith('.css') else x for x in section.yuicss]).replace('/', '_')
    section.css = '_'.join([x[:-4] if x.endswith('.css') else x for x in section.css]).replace('/', '_')
    section.yuijs = '__'.join([x[:-3] if x.endswith('.js') else x for x in section.yuijs]).replace('/', '_')
    section.js = '_'.join([x[:-3] if x.endswith('.js') else x for x in section.js]).replace('/', '_')

    if section.yuicss: section.yuicss = '___yui___' + section.yuicss
    if section.css: section.css = '___local___' + section.css

    if section.yuijs: section.yuijs = '___yui___' + section.yuijs
    if section.js: section.js = '___local___' + section.js

    viewport = '<meta name="viewport" content="width=' + section.viewport + '">' if section.viewport else ''
    linkrel = '<link rel="stylesheet" type="text/css" href="/' + section.yuicss + section.css + '.css">' if section.yuicss or section.css else ''
    script = snippet('defer-js-load', {'js_file': '/' + section.yuijs + section.js + '.js'}) if section.yuijs or section.js else ''
    analytics = snippet('analytics', {'GOOGLE_ANALYTICS_UA': section.configuration['GOOGLE_ANALYTICS_UA']}) if section.configuration['GOOGLE_ANALYTICS_UA'] else ''

    header_includes = viewport + linkrel + script.replace('\t', '').replace('\n', '') + analytics.replace('\t', '').replace('\n', '')

    if header_includes:
        html = html.replace('</head>', '\t' + header_includes + '\n\t</head>', 1)

    return html.strip()

def get(content):
    '''
    Only necessary so that the DJANGO_SETTINGS_MODULE environment gets initialized
    '''
    return str(render_to_string('blank.snip', {'content': content}))

def snippet(filename, params=None):
    return render_to_string(filename + '.snip', params).strip()