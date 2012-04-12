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

import os

from framework.subsystems import utils

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.template.loaders.filesystem import Loader
from django.template.loader import render_to_string

def html(s, params):
    html = render_to_string('Default.html', params)

    s.css = s.css + s.themecss
    s.js = s.js + s.themejs

    s.yuicss, s.css, s.yuijs, s.js = (utils.unique_list(x) for x in [s.yuicss, s.css, s.yuijs, s.js])

    s.yuicss = '__'.join([x[:-4] if x.endswith('.css') else x for x in s.yuicss]).replace('/', '_')
    s.css = '_'.join([x[:-4] if x.endswith('.css') else x for x in s.css]).replace('/', '_')
    s.yuijs = '__'.join([x[:-3] if x.endswith('.js') else x for x in s.yuijs]).replace('/', '_')
    s.js = '_'.join([x[:-3] if x.endswith('.js') else x for x in s.js]).replace('/', '_')

    if s.yuicss: s.yuicss = '___yui___' + s.yuicss
    if s.css: s.css = '___local___' + s.css

    if s.yuicss or s.css:
        linkrel = '<link rel="stylesheet" type="text/css" href="/' + s.yuicss + s.css + '.css">'
        html = html.replace('</head>', '\t' + linkrel + '\n\t</head>', 1)

    return html