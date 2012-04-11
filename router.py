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

import webapp2

from framework.subsystems import section
import settings

class Router(webapp2.RequestHandler):
    def get(self, path):
        full_path = path.strip('/').lower()
        path_parts = full_path.split('/')
        path = path_parts[0]
        p_content = path_parts[1] if len(path_parts) > 1 else None
        p_action = path_parts[2] if len(path_parts) > 2 else None
        p_params = path_parts[3:] if len(path_parts) > 3 else None
        try:
            response = webapp2.Response(unicode(section.get_section(self, '/' + full_path, path, p_content, p_action, p_params)))
            response.headers['Connection'] = 'Keep-Alive'
            return response
        except Exception as inst:
            if inst[0] == 'Redirect':
                return self.redirect(unicode(inst[1]))
            elif inst[0] == 'NotFound':
                webapp2.abort(404)
            elif inst[0] == 'BadRequest':
                webapp2.abort(400)
            elif inst[0] == 'Forbidden':
                webapp2.abort(403)
            elif inst[0] == 'AccessDenied':
                webapp2.abort(403)
            elif settings.DEBUG:
                return webapp2.Response('RouterError: ' + unicode(inst) + '\n\n' + traceback.format_exc())
            else:
                webapp2.abort(400)

    def post(self, path):
        return self.get(path)

app = webapp2.WSGIApplication([('(/.*)', Router)], debug=settings.DEBUG)