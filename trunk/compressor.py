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
from framework.subsystems import utils
import settings

class Compressor(webapp2.RequestHandler):
    def get(self, path):     
        try:
            path = path.strip('/').replace(' ', '').lower().strip()
            path, extension = os.path.splitext(path)

            contents = cache.get('compressed-' + path + extension)

            if not contents:
                filenames = [(x + extension) for x in path.split('_')]
                if len(filenames) != len(utils.unique_list(filenames)):
                    webapp2.abort(404)
                files = utils.file_search(filenames)
                contents = '\n'.join([open(f, 'r').read() for f in files])
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