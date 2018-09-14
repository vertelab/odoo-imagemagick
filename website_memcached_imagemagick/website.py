# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, Open Source Management Solution, third party addon
# Copyright (C) 2018- Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
import openerp
from openerp import http
from openerp.addons.web.http import request
from openerp.addons.website_memcached import memcached

from openerp.addons.website_imagemagick.image_recipe import website_imagemagic

import logging
_logger = logging.getLogger(__name__)


class image_recipe(models.Model):
    _inherit = "image.recipe"

    @api.multi
    def write(self, vals):
        for recipe in self:
            for key in memcached.get_keys(flush_type='imagemagick %s-%s' %(recipe.name, recipe.id), db=self.env.cr.dbname):
                memcached.mc_delete(key)
        return super(image_recipe, self).write(vals)


class Website(models.Model):
    _inherit = 'website'

    def get_kw_imagemagick(self, kw):
        if kw.get('recipe', None):
            return '%s-%s' %(kw['recipe'].name, kw['recipe'].id)
        if kw.get('recipe_ref', None):
            recipe = self.env.ref(kw['recipe_ref'])
            return '%s-%s' %(recipe.name, recipe.id)
        return ''


class CachedImageMagick(website_imagemagic):

    #~ @http.route(['/imagemagick/<model("ir.attachment"):image>/id/<model("image.recipe"):recipe>',
                 #~ '/imagemagick/<model("ir.attachment"):image>/ref/<string:recipe_id>'], type='http', auth="public", website=True)
    @memcached.route(flush_type=lambda kw: 'imagemagick %s' %request.website.get_kw_imagemagick(kw) ,binary=True, key=lambda k: '{db},{path},{lang},{device_type}', max_age=31536000, cache_age=60*60*24*30)
    def view_attachment(self, image=None, recipe=None, recipe_ref=None, **post):
        return super(CachedImageMagick, self).view_attachment(image, recipe, recipe_ref, **post)


    #~ @http.route(['/imageurl/<string:url>/id/<model("image.recipe"):recipe>','/imageurl/<string:url>/ref/<string:recipe>'], type='http', auth="public", website=True)
    @memcached.route(flush_type=lambda kw: 'imagemagick %s' %request.website.get_kw_imagemagick(kw), binary=True, key=lambda k: '{db},{path},{lang},{device_type}', max_age=31536000, cache_age=60*60*24*30)
    def view_url(self, url=None, recipe=None, recipe_ref=None, **post):
        return super(CachedImageMagick, self).view_url(recipe, recipe_ref, **post)

    #~ @http.route([
        #~ '/imagefield/<model>/<field>/<id>/ref/<recipe_ref>',
        #~ '/imagefield/<model>/<field>/<id>/id/<model("image.recipe"):recipe>',
        #~ ], type='http', auth="public", website=True, multilang=False)
    @memcached.route(flush_type=lambda kw: 'imagemagick %s' %request.website.get_kw_imagemagick(kw), binary=True, key=lambda k: '{db},{path},{lang},{device_type}', max_age=31536000, cache_age=60*60*24*30)
    def website_image(self, model, id, field, recipe=None,recipe_ref=None, **post):
        return super(CachedImageMagick, self).website_image(model, id, field, recipe,recipe_ref, **post)

    #~ @http.route([
        #~ '/imagefieldurl/<model>/<field>/<id>/ref/<recipe_ref>',
        #~ '/imagefieldurl/<model>/<field>/<id>/id/<model("image.recipe"):recipe>',
        #~ ], type='http', auth="public", website=True, multilang=False)
    @memcached.route(flush_type=lambda kw: 'imagemagick %s' %request.website.get_kw_imagemagick(kw), binary=True, key=lambda k: '{db},{path},{lang},{device_type}', max_age=31536000, cache_age=60*60*24*30)
    def website_url(self, model, id, field, recipe=None,recipe_ref=None, **post):
        return super(CachedImageMagick, self).website_url(model, id, field, recipe,recipe_ref, **post)


    #~ @http.route([
        #~ '/website/imagemagick/<model>/<field>/<id>/<model("image.recipe"):recipe>',
        #~ ], type='http', auth="public", website=True, multilang=False)
    @memcached.route(flush_type=lambda kw: 'imagemagick %s' %request.website.get_kw_imagemagick(kw), binary=True, key=lambda k: '{db},{path},{lang},{device_type}', max_age=31536000, cache_age=60*60*24*30)
    def website_imagemagick(self, model, field, id, recipe=None, **post):
        return super(CachedImageMagick, self).website_imagemagick(model, field, id, recipe, **post)


    @memcached.route([
        # ~ '/imagefield/<model>/<field>/<id>/ref/<recipe_ref>/image/<file_name>'
        ], flush_type=lambda kw: 'imagemagick', no_cache=False, binary=True, key=lambda k: '{db},{path},{lang},{device_type}', max_age=31536000, cache_age=60*60*24*30)
    def website_image_hash(self, model, id, field, recipe_ref, file_name=None, **post):
        return super(CachedImageMagick, self).website_image_hash(model, id, field, recipe_ref, **post)

                
