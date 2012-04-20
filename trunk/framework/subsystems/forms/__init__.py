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

import types

class form:
    
    def __init__(self, action = '/'):
        self.action = action
        self.controls = []
        
    def add_control(self, control):
        self.controls.append(control)
        
    def __unicode__(self):
        out = '<form method="POST" action="' + self.action + '">'
        for c in self.controls:
            out += unicode(c)
        out += '</form>'
        return out
        
class control:
    
    def __init__(self, itype, name, value=None, label=None, width=None, length=None):
        self.itype = itype
        self.name = name
        self.value = value
        self.label = label
        self.width = width
        self.length = length
        
    def __str__(self):
        out = ('<label for="' + self.name + '">' + self.label + '</label>') if self.label else ''
        out += '<input type="' + self.itype + '" name="' + self.name + '" id="' + self.name + '"'
        if self.value: out += ' value="' + self.value + '"'
        if self.length: out += ' length="' + self.length + '"'
        style = ''
        if self.width:
            style += ' width:' + unicode(self.width) + '%'
        elif self.itype == 'text':
            style += ' width:20%'
        if style: out += ' style="' + style.strip() + '"'
        out += '>'
        return out
        
class selectcontrol(control):
    
    def __init__(self, name, items=[], value=None, label=None):
        self.name = name
        self.items = items
        self.value = value
        self.label = label
        
    def __str__(self):
        out = ('<label for="' + self.name + '">' + self.label + '</label>') if self.label else ''
        out += '<select name="' + self.name + '" id="' + self.name + '">'
        for i in self.items:
            if isinstance(i[1], types.ListType):
                out += '<optgroup label="' + i[0] + '">'
                for j in i[1]:
                    out += '<option value="' + unicode(j[0]) + '"'
                    if self.value == j[0]: out += ' selected'
                    out += '>' + j[1] + '</option>'
                out += '</optgroup>'
            else:
                out += '<option value="' + unicode(i[0]) + '"'
                if self.value == i[0]: out += ' selected'
                out += '>' + unicode(i[1]) + '</option>'
        out += '</select>'
        return out
        
class textareacontrol(control):
    
    def __init__(self, name, value=None, label=None, width=None, rows=None, section_for_rte=None):
        self.name = name
        self.value = value
        self.label = label
        self.width = width
        self.rows = rows
        self.section_for_rte = section_for_rte
        
    def __str__(self):
        if(self.section_for_rte):
            self.section_for_rte.yuijs.append('yui/yui.js')
            self.section_for_rte.js.append('rte.js')
        out = ('<label for="' + self.name + '">' + self.label + '</label>') if self.label else ''
        out += '<textarea name="' + self.name + '" id="' + self.name + '"'
        if self.width: out += ' style="width:' + unicode(self.width) + '%"'
        if self.rows: out += ' rows="' + unicode(self.rows) + '"'
        if(self.section_for_rte): out += ' class="rich-text-editor"'
        out += '>'
        if self.value: out += self.value
        out += '</textarea>'
        return out
        
class checkboxcontrol(control):
    
    def __init__(self, name, value=False, label=None):
        self.name = name
        self.value = value
        self.label = label
        
    def __str__(self):
        out = ('<label for="' + self.name + '">' + self.label + '</label>') if self.label else ''
        out += '<input type="checkbox" name="' + self.name + '" id="' + self.name + '"'
        if self.value: out += ' checked'
        out += '>'
        return out