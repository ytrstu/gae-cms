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

from framework.subsystems import utils

DEBUG = True

INSTALLED_APPS = ('framework',)

TEMPLATE_DIRS = []
for d in utils.dir_search(['templates']):
    TEMPLATE_DIRS.append(d)

CONSTANTS = {
             'SITE_HEADER': 'gae-cms',
             'SITE_SUB_HEADER': 'Python-based Content Management System for Google App Engine',
             }