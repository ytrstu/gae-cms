"""
@org: GAE-CMS.COM
@description: Python-based CMS designed for Google App Engine
@(c): gae-cms.com 2012
@author: Imran Somji
@license: GNU GPL v2

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

from framework.subsystems import configuration
from framework.subsystems import cache
from framework.subsystems.theme import is_local_theme_namespace, get_custom_theme
from framework.subsystems import utils
from framework.subsystems.utils.cssmin import cssmin

class Compressor(webapp2.RequestHandler):
    def get(self, path):     
        try:
            path = path.strip('/')
            path, extension = os.path.splitext(path)

            contents = cache.get(path + extension)

            if not contents:
                contents = ''

                ''' YUI '''
                yui_parts = '' if path.find('___yui___') < 0 else path[path.find('___yui___'):].replace('___yui___', '', 1)
                yui_parts = yui_parts if yui_parts.find('___') < 0 else yui_parts[:yui_parts.find('___')]
                rest_parts = path.replace('___yui___', '', 1).replace(yui_parts, '', 1).replace('___local___', '', 1)
                if '___theme___' in rest_parts:
                    local_parts, theme_parts = rest_parts.split('___theme___')
                else:
                    local_parts, theme_parts = rest_parts, None
                if yui_parts:
                    yui_version = '3.5.0/build/'
                    yui_absolute = 'http://yui.yahooapis.com/combo?'
                    yui_parts = yui_parts.split('__')
                    yui_parts = [(yui_version + x.replace('_', '/') + '-min' + extension) for x in yui_parts]
                    result = urlfetch.fetch(yui_absolute + '&'.join(yui_parts))
                    if result.status_code == 200:
                        contents += result.content
                    else:
                        webapp2.abort(404)

                ''' Local '''
                filenames = [(x + extension) for x in local_parts.split('_')]
                if len(filenames) != len(utils.unique_list(filenames)):
                    webapp2.abort(404)
                files = utils.file_search(filenames)
                if extension == '.css':
                    contents += (''.join([cssmin(open(f, 'r').read()) for f in files])).strip()
                else:
                    contents += (''.join([open(f, 'r').read() for f in files])).strip()

                ''' Theme '''
                if theme_parts:
                    theme_namespace, theme_parts = theme_parts.split('___')
                    filenames = [(x + extension) for x in theme_parts.split('_')]
                    if len(filenames) != len(utils.unique_list(filenames)):
                        webapp2.abort(404)

                    if is_local_theme_namespace(theme_namespace):
                        if extension == '.css':
                            contents += (''.join([cssmin(open('./themes/' + theme_namespace + '/' + extension.strip('.') + '/' + f, 'r').read()) for f in filenames])).strip()
                        else:
                            contents += (''.join([open('./themes/' + theme_namespace + '/' + extension.strip('.') + '/' + f, 'r').read() for f in filenames])).strip()
                    else:
                        t = get_custom_theme(theme_namespace)
                        for f in filenames:
                            if extension == '.css':
                                index = t.css_filenames.index(f)
                                contents += cssmin(t.css_contents[index])
                            elif extension == '.js':
                                index = t.js_filenames.index(f)
                                contents += t.js_contents[index]

                cache.set(path + extension, contents)

            content_type = 'application/javascript' if extension == '.js' else 'text/css'
            response = webapp2.Response(contents, content_type=content_type)
            response.headers['Connection'] = 'Keep-Alive'
            response.set_status(200)
            return response
        except Exception as inst:
            if configuration.debug_mode():
                return webapp2.Response('RouterError: ' + unicode(inst) + '\n\n' + traceback.format_exc())
            webapp2.abort(404)

    def post(self, path):
        return self.get(path)

app = webapp2.WSGIApplication([('(/.*)', Compressor)])