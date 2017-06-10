# -*- coding: utf-8 -*-
# Author: Tanja Orme
# Date: 06/2017
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Inspired by the mdx_gist.py that comes with Nikola :)  and the gallery-directive.py

"""
Nikola markdown extension for embedded galleries.
Basic Example:
    Name of the gallery (folder):
    [:gallery: picture_of_my_dog]
"""

from __future__ import print_function, unicode_literals
from nikola.plugin_categories import MarkdownExtension
try:
    from markdown import markdown
    from markdown.extensions import Extension
    from markdown.inlinepatterns import Pattern
    from markdown.util import AtomicString
    from markdown.util import etree
    import os
    import json
    import glob
    import lxml
    from nikola.utils import LocaleBorg
    from docutils import nodes


except ImportError:
    # No need to catch this, if you try to use this without Markdown,
    # the markdown compiler will fail first
    Pattern = Extension = object

GALLERY_RE = r'\[:gallery:\s*(?P<galleryname>\S+)?\s*\]'

class GalleryPattern(Pattern):

    def __init__(self, pattern, configs):
        """Initialize pattern."""
        Pattern.__init__(self, pattern)

    def handleMatch(self, m):
        """Handle pattern matches."""
        gallery_name = m.group('galleryname').strip()
        kw = {
            'output_folder': self.site.config['OUTPUT_FOLDER'],
        }
        gallery_folder = os.path.dirname(os.path.join(self.site.path('gallery', gallery_name)))
        gallery_index_file = os.path.join(kw['output_folder'], self.site.path('gallery', gallery_name))
        with open(gallery_index_file, 'r') as inf:
            data = inf.read()
        dom = lxml.html.fromstring(data)
        text = [e.text for e in dom.xpath('//script') if e.text and 'jsonContent = ' in e.text][0]
        photo_array = json.loads(text.split(' = ', 1)[1].split(';', 1)[0])

        gallery_elem = etree.Element('div')
        gallery_elem.set('id', 'gallery-container')
        gallery_row = etree.SubElement(gallery_elem, 'div')
        gallery_row.set('class', 'row')
        for img in photo_array:
            img['url'] = '/' + '/'.join([gallery_folder, img['url']])
            img['url_thumb'] = '/' + '/'.join([gallery_folder, img['url_thumb']])
            img_elem = etree.SubElement(gallery_row, 'div')
            img_elem.set('class', 'col-xs-6 col-md-3')
            img_url = etree.SubElement(img_elem,'a')
            img_url.set('href',img['url'])
            img_url.set('class','thumbnail image-reference')
            img_src = etree.SubElement(img_url,'img')
            img_src.set('src',img['url_thumb'])
        return gallery_elem


class GalleryExtension(MarkdownExtension, Extension):
    """Gallery extension for Markdown."""

    def __init__(self, configs={}):
        """Initialize extension."""
        # set extension defaults
        self.config = {}

        # Override defaults with user settings
        for key, value in configs:
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        """Extend Markdown."""
        gallery_md_pattern = GalleryPattern(GALLERY_RE, self.getConfigs())
        gallery_md_pattern.md = md
        md.inlinePatterns.add('gallery', gallery_md_pattern, "<not_strong")
        md.registerExtension(self)

    def set_site(self, site):
        self.site = site
        self.inject_dependency('render_posts', 'render_galleries')
        GalleryPattern.site = site
        return super(MarkdownExtension, self).set_site(site)


def makeExtension(configs=None):  # pragma: no cover
    """Make Markdown extension."""
    return GalleryExtension(configs)


if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=(doctest.NORMALIZE_WHITESPACE +
                                 doctest.REPORT_NDIFF))
