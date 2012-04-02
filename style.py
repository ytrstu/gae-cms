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

import webapp2

class Style(webapp2.RequestHandler):
    def get(self, path):
        try:
            path = path.split('.')[0].strip('/').replace('-', '/').lower().strip()
            path = [x + '.css' for x in path.split('_')]
            css = ''
            for p in path:
                css += open(p, 'r').read()
            return webapp2.Response(css, content_type='text/css')
        except:
            webapp2.abort(404)
            
    def post(self, path):
        return self.get(path)
        
app = webapp2.WSGIApplication([('(/.*)', Style)])