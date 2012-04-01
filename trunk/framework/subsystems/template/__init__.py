"""
GAE-Python-CMS: Python-based CMS designed for Google AppEngine
Copyright (C) 2012  Imran Somji

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

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import importlib

register = webapp.template.create_template_register()

@register.filter
def view(path, param_string):
    mod, view = [x.strip() for x in param_string.split(',')]
    try:
        m = importlib.import_module('framework.modules.' + mod)
        view = getattr(m, 'view_' + view)
        return view(path)
    except Exception as inst:
        return 'Error: View does not exist: ' + str(inst)

def html(params):
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '../../theme/templates/Default.html')
    return template.render(path, params)