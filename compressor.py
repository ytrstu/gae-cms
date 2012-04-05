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

import webapp2, os, traceback

from framework.subsystems import cache
import settings

class Compressor(webapp2.RequestHandler):
    def get(self, path):     
        try:
            path = path.strip('/').replace(' ', '').replace('+', '/').lower().strip()
            path, extension = os.path.splitext(path)

            contents = cache.get('compressed-' + path + extension)
            if not contents:
                filenames = [(x + extension) for x in path.split('|')]
                contents = '\n'.join([open(f, 'r').read() for f in filenames])
                cache.set('compressed-' + path + extension, contents)

            response = webapp2.Response(contents.strip(), content_type='text/css')
            response.headers['Connection'] = 'Keep-Alive'
            return response
        except Exception as inst:
            if settings.DEBUG:
                return webapp2.Response('RouterError: ' + str(inst) + '\n\n' + traceback.format_exc())
            webapp2.abort(404)

    def post(self, path):
        return self.get(path)

app = webapp2.WSGIApplication([('(/.*)', Compressor)])