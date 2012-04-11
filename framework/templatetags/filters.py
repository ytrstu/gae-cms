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

from django.template import Library
import importlib, traceback

from framework.subsystems import permission
import framework.content as content
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
        elif location_id in section.location_ids:
            raise Exception('This view has a duplicate location_id to one already defined in this theme')
        else:
            section.location_ids.append(location_id)

        m = importlib.import_module('framework.content.' + mod.lower())
        contentmod = getattr(m, mod)(scope=scope, section_path=section.path, location_id=location_id, rank=None).init(section)
        item = getattr(contentmod, 'get_else_create')(scope, section.path, location_id, rank=None)

        if permission.view_content(item, section, view):
            manage = getattr(contentmod, 'get_manage_links')(item)
            view = getattr(contentmod, 'view_' + view)(item, params)
            return manage + view
        else:
            raise Exception('You do not have permission to view this content')
    except Exception as inst:
        error = unicode(inst) + ('<div class="traceback">' + traceback.format_exc().replace('\n', '<br><br>') + '</div>') if settings.DEBUG else ''
        return '<div class="status error">Error: View does not exist: %s</div>' % error

@register.filter
def joinby(value, arg):
    return arg.join(value)