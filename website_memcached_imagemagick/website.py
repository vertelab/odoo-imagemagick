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


from odoo import http
from odoo.http import request
from odoo.service import common
from odoo.addons.website_memcached import memcached
from odoo import models, fields, api, _

from odoo.addons.website_imagemagick.image_recipe import website_imagemagic

import logging
_logger = logging.getLogger(__name__)



# class image_recipe(models.Model):
#     _inherit = "image.recipe"

#     def write(self, vals):
#         for key in memcached.get_keys(flush_type='imagemagick %s-%s' %(self.name, self.id)):
#             memcached.mc_delete(key)
# #         return super(image_recipe, self).write(vals)


# class Website(models.Model):
#     _inherit = 'website'

#     def get_kw_imagemagick(self, kw):
#         if kw.get('recipe', None):
#             return '%s-%s' %(kw['recipe'].name, kw['recipe'].id)
#         if kw.get('recipe_ref', None):
#             recipe = self.env.ref(kw['recipe_ref'])
#             return '%s-%s' %(recipe.name, recipe.id)
#         return ''


class CachedImageMagick(website_imagemagic):

    #~ @http.route(['/imagemagick/<model("ir.attachment"):image>/id/<model("image.recipe"):recipe>',
                 #~ '/imagemagick/<model("ir.attachment"):image>/ref/<string:recipe_id>'], type='http', auth="public", website=True)
    @memcached.route(
        key=lambda parameters: 'db: {db} path: {path}',

        # key=lambda parameters: 'hej',

        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def view_attachment(self, image=None, recipe=None, recipe_ref=None, **post):
        return super(CachedImageMagick, self).view_attachment(image, recipe, recipe_ref, **post)




    #~ @http.route(['/imageurl/<string:url>/id/<model("image.recipe"):recipe>','/imageurl/<string:url>/ref/<string:recipe>'], type='http', auth="public", website=True)
    @memcached.route(
        key=lambda parameters: 'db: {db} path: {path}',

        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def view_url(self, url=None, recipe=None, recipe_ref=None, **post):
        return super(CachedImageMagick, self).view_url(recipe, recipe_ref, **post)


    # @memcached.route(
    #     # key=lambda parameters: 'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country} search: %s group: %s pricelist: %s attribs: %s' % (str(parameters.get("search")), request.website.get_dn_groups(), request.website.get_pricelist(), request.website.get_attribs()),
    #     key=lambda parameters: 'hej',

    #     flush_type=lambda kw: 'webshop',
    #     no_cache=True,
    #     cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
    #     max_age=31536000, # Webbläsare
    #     s_maxage=600)     # Varnish
    # def website_image(self, model, id, field, recipe=None,recipe_ref=None, **post):
    #     return super(CachedImageMagick, self).website_image(model, id, field, recipe,recipe_ref, **post)


    # @memcached.route(
    #     # key=lambda parameters: 'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country} search: %s group: %s pricelist: %s attribs: %s' % (str(parameters.get("search")), request.website.get_dn_groups(), request.website.get_pricelist(), request.website.get_attribs()),
    #     key=lambda parameters: 'hej',

    #     flush_type=lambda kw: 'webshop',
    #     no_cache=True,
    #     cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
    #     max_age=31536000, # Webbläsare
    #     s_maxage=600)     # Varnish
    def website_url(self, model, id, field, recipe=None,recipe_ref=None, **post):
        return super(CachedImageMagick, self).website_url(model, id, field, recipe,recipe_ref, **post)


    #~ @http.route([
        #~ '/website/imagemagick/<model>/<field>/<id>/<model("image.recipe"):recipe>',
        #~ ], type='http', auth="public", website=True, multilang=False)

    @memcached.route(
        key=lambda parameters: 'db: {db} path: {path}',

        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def website_imagemagick(self, model, field, id, recipe=None, **post):
        return super(CachedImageMagick, self).website_imagemagick(model, field, id, recipe, **post)
