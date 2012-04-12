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

import traceback

from django.template import Library

import framework.content as content
from framework.subsystems.section import MAIN_CONTAINER_LOCATION_ID
import settings

register = Library()

@register.filter
def view(section, param_string):
    params = [x.strip() for x in param_string.split(',')]
    try:
        try:
            scope, location_id, mod, view = params[0:4]
        except:
            raise Exception('A minimum of four parameters required')
        else:
            params = params[4:] if len(params) > 4 else None

        if scope not in [content.SCOPE_GLOBAL, content.SCOPE_LOCAL]:
            raise Exception('Scope must be one of: ' + str([content.SCOPE_GLOBAL, content.SCOPE_LOCAL]))
        elif '-' in location_id or ' ' in location_id:
            raise Exception('Invalid character "-" or " " for location_id')
        elif location_id == MAIN_CONTAINER_LOCATION_ID:
            raise Exception('"%s" is a reserved location_id' % MAIN_CONTAINER_LOCATION_ID)
        return section.get_view(scope, location_id, mod, view, params)
    except Exception as inst:
        error = unicode(inst) + ('<div class="traceback">' + traceback.format_exc().replace('\n', '<br><br>') + '</div>') if settings.DEBUG else ''
        return '<div class="status error">Error: View does not exist: %s</div>' % error

@register.filter
def joinby(value, arg):
    return arg.join(value)

@register.filter
def yuicss(section, args):
    [section.yuicss.append(x.strip('/ ')) for x in args.split(',')]
    return ''

@register.filter
def themecss(section, args):
    [section.themecss.append(x.strip('/ ')) for x in args.split(',')]
    return ''

@register.filter
def css(section, args):
    [section.css.append(x.strip('/ ')) for x in args.split(',')]
    return ''

@register.filter
def yuijs(section, args):
    [section.yuijs.append(x.strip('/ ')) for x in args.split(',')]
    return ''

@register.filter
def js(section, args):
    [section.js.append(x.strip('/ ')) for x in args.split(',')]
    return ''