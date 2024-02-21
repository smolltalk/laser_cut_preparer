#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) 2024 Sebastien Morvan, morvan.sebastien@gmail.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
"""
This extension prepares the document for the laser cutting by:
- setting the stroke width to 0.01mm
- fixing colors to those recognized by the laser cutting machine,
  i.e. all combinations of 255 and 0.
"""

#!/usr/bin/env python
import inkex
import coloreffect

class LaserCutPreparerEffect(coloreffect.ColorEffect):
  def __init__(self):
    coloreffect.ColorEffect.__init__(self)
    opts = [('-c', '--fix_colors', 'inkbool', 'fix_colors', False,
             'Fix colors'),
             ('-w', '--fix_stroke_width', 'inkbool', 'fix_stroke_width', False,
             'Fix stroke width'),
            ]
    for o in opts:
        self.OptionParser.add_option(o[0], o[1], action="store", type=o[2],
                                     dest=o[3], default=o[4], help=o[5])

    self.visited = []
    self.stroke_props = ('stroke-width',)  

  def colmod(self, r, g, b):
    r = 255 if r > 127 else 0
    g = 255 if g > 127 else 0
    b = 255 if b > 127 else 0
    
    return '%02x%02x%02x' % (r,g,b)

  def changeStyle(self, node):
    # Fix colors?
    if self.options.fix_colors:
      self.changeStyleColors(node)
  
    # Fix stroke width?
    if self.options.fix_stroke_width:
      self.changeStyleStrokeWidth(node)
  
  def changeStyleColors(self, node):
    coloreffect.ColorEffect.changeStyle(self, node)

  def changeStyleStrokeWidth(self, node):  
    for attr in self.stroke_props:
        val = node.get(attr)
        if val:
            new_val = self.process_stroke_width()
            if new_val != val:
                node.set(attr, new_val)

    if node.attrib.has_key('style'):
        # References for style attribute:
        # http://www.w3.org/TR/SVG11/styling.html#StyleAttribute,
        # http://www.w3.org/TR/CSS21/syndata.html
        #
        # The SVG spec is ambiguous as to how style attributes should be parsed.
        # For example, it isn't clear whether semicolons are allowed to appear
        # within strings or comments, or indeed whether comments are allowed to
        # appear at all.
        #
        # The processing here is just something simple that should usually work,
        # without trying too hard to get everything right.
        # (Won't work for the pathological case that someone escapes a property
        # name, probably does the wrong thing if colon or semicolon is used inside
        # a comment or string value.)
        style = node.get('style') # fixme: this will break for presentation attributes!
        if style:
            # inkex.debug('old style:'+style)
            declarations = style.split(';')
            for i,decl in enumerate(declarations):
                parts = decl.split(':', 2)
                if len(parts) == 2:
                    (prop, val) = parts
                    prop = prop.strip().lower()
                    if prop in self.stroke_props:
                        val = val.strip()
                        new_val = self.process_stroke_width()
                        if new_val != val:
                            declarations[i] = prop + ':' + new_val
            # inkex.debug('new style:'+';'.join(declarations))
            node.set('style', ';'.join(declarations))

  def process_stroke_width(self):
    return '0.01'


if __name__ == '__main__':
  laser_cut_preparer_effect = LaserCutPreparerEffect()
  laser_cut_preparer_effect.affect()

