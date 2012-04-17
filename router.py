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
from framework.subsystems import template
import settings

class Router(webapp2.RequestHandler):
    def get(self, path):
        try:
            response = webapp2.Response(unicode(section.get_section(self, path)))
            response.headers['Connection'] = 'Keep-Alive'
            return response
        except Exception as inst:
            if inst[0] == 'Redirect':
                return self.redirect(str(inst[1]))
            elif inst[0] == 'NotFound':
                err = 404
                main = 'Page not found'
            elif inst[0] == 'BadRequest':
                err = 400
                main = 'Bad Request'
            elif inst[0] == 'Forbidden':
                err = 403
                main = 'Forbidden'
            elif inst[0] == 'AccessDenied':
                err = 403
                main = 'Access Denied'
            elif settings.DEBUG:
                err = 400
                main = 'RouterError: ' + unicode(inst) + '<div class="traceback">' + traceback.format_exc().replace('\n', '<br><br>') + '</div>'
            else:
                err = 400
                main = 'An error has occurred.'
            default_section = section.get_section(None, '')
            response = webapp2.Response(unicode(template.html(default_section, '<div class="status error">' + main + '</div>')))
            response.set_status(err)
            return response

    def post(self, path):
        return self.get(path)

app = webapp2.WSGIApplication([('(/.*)', Router)], debug=settings.DEBUG)