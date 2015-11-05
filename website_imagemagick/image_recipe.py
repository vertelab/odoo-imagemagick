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
import base64
from cStringIO import StringIO
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import http
from openerp.http import request
from openerp import SUPERUSER_ID
from datetime import datetime
from openerp.modules import get_module_resource, get_module_path
import werkzeug
import pytz
import re
import hashlib

from openerp.tools.safe_eval import safe_eval as eval

from wand.image import Image
from wand.display import display
from wand.drawing import Drawing
import subprocess

import logging
_logger = logging.getLogger(__name__)

class website_imagemagic(http.Controller):

    # this controller will control url: /image/image_id/magic/recipe_id
    @http.route(['/imagemagick/<model("ir.attachment"):image>/id/<model("image.recipe"):recipe>',
                 '/imagemagick/<model("ir.attachment"):image>/ref/<string:recipe_id>'], type='http', auth="public", website=True)
    def view_attachment(self, image=None, recipe=None, recipe_ref=None, **post):
        if recipe_ref:
            recipe = request.env.ref(recipe_ref)
        if recipe:
            return recipe.send_file(http, attachment=image)
        return request.registry['website']._image(
                request.cr, request.uid, 'ir.attachment','%s_%s' % (image.id, hashlib.sha1(image.sudo().write_date or image.sudo().create_date or '').hexdigest()[0:7]),
                'datas', werkzeug.wrappers.Response(),250,250,cache=STATIC_CACHE)

    # this controller will control url: /image/image_url/magic/recipe_id
    @http.route(['/imageurl/<string:url>/id/<model("image.recipe"):recipe>','/imageurl/<string:url>/ref/<string:recipe>'], type='http', auth="public", website=True)
    def view_url(self, url=None, recipe=None, recipe_ref=None, **post):
        if recipe_ref:
            recipe = request.env.ref(recipe_ref) # 'imagemagick.my_recipe'
        return recipe.send_file(http, url=url)


    @http.route([
        '/imagefield/<model>/<field>/<id>/ref/<recipe_ref>',
        '/imagefield/<model>/<field>/<id>/id/<model("image.recipe"):recipe>',
        #~ '/imageobj/<>/ref/<string:recipe>'

        ], type='http', auth="public", website=True, multilang=False)
    def website_image(self, model, id, field, recipe=None,recipe_ref=None):
        if recipe_ref:
            recipe = request.env.ref(recipe_ref) # 'imagemagick.my_recipe'
        #~ recipe.send_file(http,field=field,model=model,id=id.split('_')[0])
        return recipe.send_file(http,field=field,model=model,id=id)


        try:
            idsha = id.split('_')
            id = idsha[0]
            response = werkzeug.wrappers.Response()
            return request.registry['website']._image(
                request.cr, request.uid, model, id, field, response, max_width, max_height,
                cache=STATIC_CACHE if len(idsha) > 1 else None)
        except Exception:
            _logger.exception("Cannot render image field %r of record %s[%s] at size(%s,%s)",
                             field, model, id, max_width, max_height)
            response = werkzeug.wrappers.Response()
            return self.placeholder(response)

class website(models.Model):
    _inherit = 'website'

    #~ def _image_placeholder(self, response):
        #~ """
        #~ Choose placeholder.
        #~ """
        #~ # file_open may return a StringIO. StringIO can be closed but are
        #~ # not context managers in Python 2 though that is fixed in 3
        #~ with contextlib.closing(openerp.tools.misc.file_open(
                #~ os.path.join('web', 'static', 'src', 'img', 'placeholder.png'),
                #~ mode='rb')) as f:
            #~ response.data = f.read()
            #~ return response.make_conditional(request.httprequest)

    def imagemagick_url(self, record, field, recipe):
        """Returns a local url that points to the image field of a given browse record."""
        return '/imagefield/%s/%s/%s/ref/%s' % (record._name, field, record.sudo().id, recipe)

    # WIP. Very temporary solution.
    def imagemagick(self, model, id, field, recipe, response, cache=None):
        """ Fetches the requested field and applies the given imagemagick recipe on it.

        ???Resizing is bypassed if the object provides a $field_big, which will
        be interpreted as a pre-resized version of the base field.???

        If the record is not found or does not have the requested field,
        returns a placeholder image via :meth:`~._image_placeholder`.

        Sets and checks conditional response parameters:
        * :mailheader:`ETag` is always set (and checked)
        * :mailheader:`Last-Modified is set iif the record has a concurrency
          field (``__last_update``)

        The requested field is assumed to be base64-encoded image data in
        all cases.
        """

        return recipe.send_file(http,field=field,model=model,id=id)

        Model = self.pool[model]
        id = int(id)

        ids = Model.search(cr, uid,
                           [('id', '=', id)], context=context)
        if not ids and 'website_published' in Model._fields:
            ids = Model.search(cr, openerp.SUPERUSER_ID,
                               [('id', '=', id), ('website_published', '=', True)], context=context)
        if not ids:
            return self._image_placeholder(response)

        concurrency = '__last_update'
        [record] = Model.read(cr, openerp.SUPERUSER_ID, [id],
                              [concurrency, field],
                              context=context)

        if concurrency in record:
            server_format = openerp.tools.misc.DEFAULT_SERVER_DATETIME_FORMAT
            try:
                response.last_modified = datetime.datetime.strptime(
                    record[concurrency], server_format + '.%f')
            except ValueError:
                # just in case we have a timestamp without microseconds
                response.last_modified = datetime.datetime.strptime(
                    record[concurrency], server_format)

        # Field does not exist on model or field set to False
        if not record.get(field):
            # FIXME: maybe a field which does not exist should be a 404?
            return self._image_placeholder(response)

        response.set_etag(hashlib.sha1(record[field]).hexdigest())
        response.make_conditional(request.httprequest)

        if cache:
            response.cache_control.max_age = cache
            response.expires = int(time.time() + cache)

        # conditional request match
        if response.status_code == 304:
            return response

        data = record[field].decode('base64')
        image = Image.open(cStringIO.StringIO(data))
        response.mimetype = Image.MIME[image.format]

        filename = '%s_%s.%s' % (model.replace('.', '_'), id, str(image.format).lower())
        response.headers['Content-Disposition'] = 'inline; filename="%s"' % filename

        if (not max_width) and (not max_height):
            response.data = data
            return response

        w, h = image.size
        max_w = int(max_width) if max_width else maxint
        max_h = int(max_height) if max_height else maxint

        if w < max_w and h < max_h:
            response.data = data
        else:
            size = (max_w, max_h)
            img = image_resize_and_sharpen(image, size, preserve_aspect_ratio=True)
            image_save_for_web(img, response.stream, format=image.format)
            # invalidate content-length computed by make_conditional as
            # writing to response.stream does not do it (as of werkzeug 0.9.3)
            del response.headers['Content-Length']

        return response

class image_recipe(models.Model):
    _name = "image.recipe"

    color = fields.Integer(string='Color Index')
    name = fields.Char(string='Name')
    recipe = fields.Text(string='Recipe')
    param_ids = fields.One2many(comodel_name='image.recipe.param', inverse_name='recipe_id', string='Recipes')

  # http://docs.wand-py.org/en/0.4.1/index.html

    def attachment_to_img(self, attachment):  # return an image object while filename is an attachment
        if attachment.url:  # make image url as /module_path/attachment_url and use it as filename
            path = '/'.join(get_module_path(attachment.url.split('/')[1]).split('/')[0:-1])
            return Image(filename=path + attachment.url)
        _logger.warning('<<<<<<<<<<<<<< attachment_to_img >>>>>>>>>>>>>>>>: %s' % attachment.datas)
        return Image(blob=attachment.datas.decode('base64'))

    def data_to_img(self, data):  # return an image object while filename is data
        _logger.warning('<<<<<<<<<<<<<< data_to_img >>>>>>>>>>>>>>>>: %s' % data)
        return Image(blob=data.decode('base64'))

    def url_to_img(self, url):  # return an image object while filename is an url
        return Image(filename=url)

    def get_mtime(self, attachment):    # return a last modified time of an image
        if attachment.write_date > self.write_date:
            return attachment.write_date
        return self.write_date

    def send_file(self, http, attachment=None, url=None,field=None,model=None,id=None):   # return a image while given an attachment or an url
        if field:
            o = self.env[model].browse(int(id))
            _logger.warning('<<<<<<<<<<<<<< data >>>>>>>>>>>>>>>>: %s' % o)
            return http.send_file(StringIO(self.run(self.data_to_img(getattr(o, field))).make_blob(format='jpg')), filename=field, mtime=self.get_mtime(o))
        if attachment:
            _logger.warning('<<<<<<<<<<<<<< attachment >>>>>>>>>>>>>>>>: %s' % attachment)
            return http.send_file(StringIO(self.run(self.attachment_to_img(attachment)).make_blob(format='jpg')), filename=attachment.datas_fname, mtime=self.get_mtime(attachment))
        return http.send_file(self.run(self.url_to_img(url)), filename=url)


    def run(self, image, **kwargs):   # return a image with specified recipe
        kwargs.update({p.name: p.value for p in self.param_ids})    #get parameters from recipe
        kwargs.update({
            'Image': Image,
            'image': image,
            'user': self.env['res.users'].browse(self._uid),
            })
        eval(self.recipe, kwargs, mode='exec', nocopy=True)
        return image

class image_recipe_param(models.Model):
    _name = "image.recipe.param"

    name = fields.Char(string='Name')
    value = fields.Char(string='Value')
    recipe_id = fields.Many2one(comodel_name='image.recipe', string='Recipe')
