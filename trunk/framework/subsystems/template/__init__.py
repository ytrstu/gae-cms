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
GNU General Public License for more detailsection.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import os

from google.appengine.api import users

import settings
from framework.subsystems import permission
from framework.subsystems import utils

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.template.loaders.filesystem import Loader
from django.template.loader import render_to_string

def html(section, main=''):
    params = {
        'CONSTANTS': settings.CONSTANTS,
        'VERSION': os.environ['CURRENT_VERSION_ID'],
        'user': users.get_current_user(),
        'is_admin': permission.is_admin(section.path),
        'section': section,
        'main': main,
    }
    html = render_to_string('Default.html', params)

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

    if section.yuicss or section.css:
        linkrel = '<link rel="stylesheet" type="text/css" href="/' + section.yuicss + section.css + '.css">'
        html = html.replace('</head>', '\t' + linkrel + '\n\t</head>', 1)

    if section.yuijs or section.js:
        script = '<script type="text/javascript" src="/' + section.yuijs + section.js + '.js"></script>'
        html = html.replace('</head>', '\t' + script + '\n\t</head>', 1)

    return html

def snippet(filename, params=None):
    return render_to_string(filename + '.snip', params)