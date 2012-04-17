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

from google.appengine.api import urlfetch

from framework.subsystems import cache
from framework.subsystems import utils
import settings

class Compressor(webapp2.RequestHandler):
    def get(self, path):     
        try:
            path = path.strip('/').replace(' ', '').lower().strip()
            path, extension = os.path.splitext(path)

            contents = cache.get(path + extension)

            if not contents:
                contents = ''
                yui_parts = '' if path.find('___yui___') < 0 else path[path.find('___yui___'):].replace('___yui___', '', 1)
                yui_parts = yui_parts if yui_parts.find('___') < 0 else yui_parts[:yui_parts.find('___')]
                local_path = path.replace('___yui___', '', 1).replace(yui_parts, '', 1).replace('___local___', '', 1)
                if yui_parts:
                    yui_version = '3.5.0/build/'
                    yui_absolute = 'http://yui.yahooapis.com/combo?'
                    yui_parts = yui_parts.split('__')
                    yui_parts = [(yui_version + x.replace('_', '/') + '-min' + extension) for x in yui_parts]
                    result = urlfetch.fetch(yui_absolute + '&'.join(yui_parts))
                    if result.status_code == 200:
                        contents += result.content + '\n\n'
                    else:
                        webapp2.abort(404)
                filenames = [(x + extension) for x in local_path.split('_')]
                if len(filenames) != len(utils.unique_list(filenames)):
                    webapp2.abort(404)
                files = utils.file_search(filenames)
                contents += ('\n'.join([open(f, 'r').read() for f in files])).strip()
                cache.set(path + extension, contents)

            content_type = 'application/javascript' if extension == '.js' else 'text/css'
            response = webapp2.Response(contents, content_type=content_type)
            response.headers['Connection'] = 'Keep-Alive'
            response.set_status(200)
            return response
        except Exception as inst:
            if settings.DEBUG:
                return webapp2.Response('RouterError: ' + unicode(inst) + '\n\n' + traceback.format_exc())
            webapp2.abort(404)

    def post(self, path):
        return self.get(path)

app = webapp2.WSGIApplication([('(/.*)', Compressor)])