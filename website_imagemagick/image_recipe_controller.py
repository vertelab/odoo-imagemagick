# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2019 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import base64
from cStringIO import StringIO
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo import http
from odoo.http import request, STATIC_CACHE
from odoo import SUPERUSER_ID
from datetime import datetime
from odoo.modules import get_module_resource, get_module_path
import werkzeug
import pytz
import re
import hashlib
import sys
import traceback

from image_recipe import Image

import logging
_logger = logging.getLogger(__name__)

# https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/image-optimization#selecting-the-right-image-format

class website_imagemagic(http.Controller):

    # this controller will control url: /image/image_id/magic/recipe_id
    @http.route(['/imagemagick/<model("ir.attachment"):image>/id/<model("image.recipe"):recipe>',
                 '/imagemagick/<model("ir.attachment"):image>/ref/<string:recipe_id>'], type='http', auth="public", website=True)
    def view_attachment(self, image=None, recipe=None, recipe_ref=None, **post):
        if recipe_ref:
            recipe = request.env.ref(recipe_ref)
        if recipe:
            return recipe.send_file(attachment=image)
        return request.registry['website']._image(
                request.cr, request.uid, 'ir.attachment','%s_%s' % (image.id, hashlib.sha1(image.sudo().write_date or image.sudo().create_date or '').hexdigest()[0:7]),
                'datas', werkzeug.wrappers.Response(),250,250,cache=STATIC_CACHE)

    # this controller will control url: /image/id/<id>?url=<your url>
    @http.route(['/imageurl/id/<model("image.recipe"):recipe>','/imageurl/ref/<string:recipe_ref>'], type='http', auth="public", website=True)
    def view_url(self, recipe=None, recipe_ref=None, **post):
        url = post.get('url','')
        if len(url)>0 and url[0] == '/':
            url=url[1:]
        if recipe_ref:
            recipe = request.env.ref(recipe_ref) # 'imagemagick.my_recipe'
        if url:
            return recipe.send_file(url='/'.join(get_module_path(url.split('/')[0]).split('/')[0:-1]) + '/' + url)
        return http.send_file(StringIO(recipe.run(Image(filename=get_module_path('web') + '/static/src/img/placeholder.png')).make_blob(format=recipe.image_format if recipe.image_format else 'png')))

    @http.route([
        '/imagefield/<model>/<field>/<id>/ref/<recipe_ref>',
        '/imagefield/<model>/<field>/<id>/id/<model("image.recipe"):recipe>',
        ], type='http', auth="public", website=True, multilang=False)
    def website_image(self, model, id, field, recipe=None, recipe_ref=None, **post):
        if recipe_ref:
            recipe = request.env.ref(recipe_ref) # 'imagemagick.my_recipe'
        return recipe.sudo().send_file(field=field, model=model, id=id)

    @http.route([
        '/imagefield/<model>/<field>/<id>/ref/<recipe_ref>/image/<file_name>'
        ], type='http', auth="public", website=True, multilang=False)
    def website_image_hash(self, model, id, field, recipe_ref, file_name=None, **post):
        if recipe_ref:
            recipe = request.env.ref(recipe_ref) # 'imagemagick.my_recipe'
        return recipe.sudo().send_file(field=field, model=model, id=id)

    @http.route([
        '/imagefieldurl/<model>/<field>/<id>/ref/<recipe_ref>',
        '/imagefieldurl/<model>/<field>/<id>/id/<model("image.recipe"):recipe>',
        ], type='http', auth="public", website=True, multilang=False)
    def website_url(self, model, id, field, recipe=None,recipe_ref=None, **post):
        if recipe_ref:
            recipe = request.env.ref(recipe_ref)
        o = request.env[model].browse(int(id))
        url = getattr(o, field).strip()
        attachment_id = int(url.split('/')[6].split('_')[0])
        return recipe.send_file(field='datas',model='ir.attachment',id=attachment_id)

    @http.route([
        '/website/imagemagick/<model>/<field>/<id>/<model("image.recipe"):recipe>',
        ], type='http', auth="public", website=True, multilang=False)
    def website_imagemagick(self, model, field, id, recipe=None, **post):
        try:
            idsha = id.split('_')
            id = idsha[0]
            response = werkzeug.wrappers.Response()
            return request.env['website']._imagemagick(
                model, id, field, recipe, response,
                cache=STATIC_CACHE if len(idsha) > 1 else None)
        except Exception:
            _logger.exception("Cannot render image field %r of record %s[%s] with recipe[%s]",
                             field, model, id, recipe.id)
            response = werkzeug.wrappers.Response()
            return self.placeholder(response)
    """
     class werkzeug.contrib.cache.FileSystemCache(cache_dir, threshold=500, default_timeout=300, mode=384)

    A cache that stores the items on the file system. This cache depends on being the only user of the cache_dir. Make absolutely sure that nobody but this cache stores files there or otherwise the cache will randomly delete files therein.
    Parameters:

        cache_dir – the directory where cache files are stored.
        threshold – the maximum number of items the cache stores before it starts deleting some.
        default_timeout – the default timeout that is used if no timeout is specified on set().
        mode – the file mode wanted for the cache files, default 0600

    """

    def placeholder(self, response):
        return request.env['website']._image_placeholder(response)

#
# Web Editor tools
#

    """
    Parameters:
    * img_src: image src for target image
    * recipe_id: recipe id of selected recipe
    """
    @http.route(['/website_imagemagick_recipe_change'], type='json', auth="public", website=True)
    def website_imagemagick_recipe_change(self, img_src, recipe_id, **kw):
        _logger.error('url %s' % img_src)
        attachment_id = 0
        url = None
        if '/website/static/src/img/' in img_src and not '/imageurl' in img_src:
            url = img_src[img_src.find('/website'):]
            return '/imageurl/id/%s?url=%s' %(recipe_id,url)
        if '/website/image/' in img_src:
            pattern = re.search('/website/image/(.*)/(.*)/(.*)', img_src)
            return '/imagefield/%s/%s/%s/ref/%s' %(pattern.group(1), pattern.group(3), pattern.group(2).split('_')[0], recipe_id)
        elif '/imagemagick/' in img_src:
            attachment_id = re.search('/imagemagick/(.*)/id', img_src).group(1)
            attachment = request.env['ir.attachment'].browse(int(attachment_id if attachment_id.isdigit() else 0))
            return '/imagemagick/%s/id/%s' %(attachment.id, recipe_id)
        else:
            attachment_id = 0
        attachment = request.env['ir.attachment'].browse(int(attachment_id  if attachment_id.isdigit() else 0))
        return '/imagefield/ir.attachment/datas/%s/id/%s' %(attachment.id, recipe_id)

    #TODO: reset recipe to normal attachment




