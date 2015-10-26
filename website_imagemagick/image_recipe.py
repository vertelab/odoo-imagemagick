# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2015 Vertel AB (<http://vertel.se>).
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
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import http
from openerp.http import request
from openerp import SUPERUSER_ID
from datetime import datetime
import werkzeug
import pytz
import re

from openerp.tools.safe_eval import safe_eval as eval

# from wand.image import Image
# from wand.drawing import Drawing



import logging
_logger = logging.getLogger(__name__)

class website_imagemagic(http.Controller):

    @http.route(['/image/<model("ir.attachment"):image>/magic/<model("image.recipe"):recipe>', ], type='http', auth="public", website=True)
    def get_products(self, image=None,recipe=None,**post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        return recipe.send_file(http,image)


class image_recipe(models.Model):
    _name = "image.recipe"
    
    name = fields.Char(string='Name', )
    recipe = fields.Text(string='Recipe', )
    param_ids = fields.One2many(comodel_name='image.recipe.param', inverse_name='recipe_id', string='Recipes')
  
  # http://docs.wand-py.org/en/0.4.1/index.html
  
    def send_file(self,http,image):
        return http.send_file(image.data, filename=image.filename, mtime=image.mtime)


    def run(self,image):
        eval(self.recipe, {
            'image': image,
            'user': self.env['res.users'].browse(self._uid),
            'result': None,
            }, mode='exec', nocopy=True)
        

class image_recipe_param(models.Model):
    _name = "image.recipe.param"
    
    name = fields.Char(string='Name', )
    value = fields.Char(string='Recipe', )
    recipe_id = fields.Many2one(comodel_name='image.recipe', string='Recipe')
