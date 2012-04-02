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
            #print str(section.get_section(self, path_parts))
            return webapp2.Response(str(section.get_section(self, path_parts)))
        except IndexError:
            try:
                section.get_section(self, [section.UNALTERABLE_HOME_PATH, None, None, None])
                webapp2.abort(404)
            except (IndexError, TypeError):
                s = str(section.create_section(self, path=section.UNALTERABLE_HOME_PATH, parent_path=None, title='GAE-Python-CMS'))
                if(path == section.UNALTERABLE_HOME_PATH):
                    return webapp2.Response(s)
                else:
                    webapp2.abort(404)
        except AttributeError as inst:
            #return webapp2.Response('RouterError: ' + str(inst))
            webapp2.abort(404)
        except Exception as inst:
            if inst[0] == 'Redirect':
                return self.redirect(inst[1])
            elif inst[0] == 'UndefinedContent':
                webapp2.abort(404)
            return webapp2.Response('RouterError: ' + str(inst))
            #webapp2.abort(403)
            
    def post(self, path):
        return self.get(path)
        
def get_path_parts(path):
    base_path = path.split('/')[0]
    path = path.lstrip(base_path).strip('/')
    module_path = path.split('/')[0]
    path = path.lstrip(module_path).strip('/')
    action_path = path.split('/')[0]
    path = path.lstrip(action_path).strip('/')
    parameter_path = path.split('/')[0]
    return base_path, module_path, action_path, parameter_path
        
app = webapp2.WSGIApplication([('(/.*)', Router)], debug=settings.DEBUG)