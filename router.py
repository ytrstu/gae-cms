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

import os, traceback

import webapp2

from framework import section
import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

class Router(webapp2.RequestHandler):
    def get(self, path):
        path = path.strip('/').lower()
        if path == section.UNALTERABLE_HOME_PATH:
            webapp2.abort(404) # Only want to access UNALTERABLE_HOME_PATH through the root
        elif not path:
            path = section.UNALTERABLE_HOME_PATH
        path_parts = get_path_parts(path)
        if path_parts[1] and not path_parts[2]: # Content is defined but no action
                webapp2.abort(404)
        try:
            response = webapp2.Response(str(section.get_section(self, path_parts)))
            response.headers['Connection'] = 'Keep-Alive'
            return response
        except Exception as inst:
            if inst[0] == 'Redirect':
                return self.redirect(inst[1])
            elif inst[0] == 'NotFound':
                webapp2.abort(404)
            elif inst[0] == 'BadRequest':
                webapp2.abort(400)
            elif inst[0] == 'Forbidden':
                webapp2.abort(403)
            elif settings.DEBUG:
                return webapp2.Response('RouterError: ' + str(inst) + '\n\n' + traceback.format_exc())
            else:
                webapp2.abort(400)

    def post(self, path):
        return self.get(path)

def get_path_parts(path):
    base_path = path.split('/')[0]
    path = path.lstrip(base_path).strip('/')
    content_path = path.split('/')[0]
    path = path.lstrip(content_path).strip('/')
    action_path = path.split('/')[0]
    path = path.lstrip(action_path).strip('/')
    parameter_path = path.split('/')[0]
    return base_path, content_path, action_path, parameter_path

app = webapp2.WSGIApplication([('(/.*)', Router)], debug=settings.DEBUG)