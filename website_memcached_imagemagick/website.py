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

class Attachment(models.Model):
    _inherit = "ir.attachment"
    
    memcached_time = fields.Datetime(string='Memcached Timestamp', default=lambda *args, **kwargs: fields.Datetime.now(), help="Last modification relevant to memcached.")
    
    @api.multi
    def write(self, values):
        for field in self.get_memcached_fields():
            if field in values:
                values['memcached_time'] = fields.Datetime.now()
                break
        return super(Attachment, self).write(values)
    
    @api.model
    def get_memcached_fields(self):
        """Return a list of fields that should trigger an update of memcached."""
        return ['type', 'datas', 'url']


class Website(models.Model):
    _inherit = 'website'

    def get_kw_imagemagick(self, kw):
        if kw.get('recipe'):
            return '%s-%s' %(kw['recipe'].name.encode('ascii', 'replace'), kw['recipe'].id)
        if kw.get('recipe_ref'):
            recipe = self.env.ref(kw['recipe_ref'])
            return '%s-%s' %(recipe.name.encode('ascii', 'replace'), recipe.id)
        return ''
    
    @api.model
    def memcached_get_model_time_field(self, obj):
        """Return the time field to use for this model."""
        if 'memcached_time' in obj._fields:
            return 'memcached_time'
        elif 'write_date' in obj._fields:
            return 'write_date'
    
    @api.multi
    def memcached_get_key_imagemagick(self, kw):
        """Build keywords to use in imagemagick cache keys."""
        times = []
        res = {
            'recipe_id': 0,
            'attachment_id': 0,
            'time': '',
            'url': kw.get('url', ''),
            'model': kw.get('model', ''),
            'id': kw.get('id', 0),
            'field': kw.get('field', ''),
            'file_name': kw.get('file_name', ''),
        }
        if kw.get('recipe'):
            times.append(kw['recipe'].write_date)
            res['recipe_id'] = kw['recipe'].id
        elif kw.get('recipe_ref'):
            recipe = self.env.ref(kw['recipe_ref'])
            times.append(recipe.write_date)
            res['recipe_id'] = recipe.id
        if kw.get('image'):
            times.append(kw['image'].memcached_time)
            res['attachment_id'] = kw['image'].id
        if 'model' in kw and 'id' in kw and 'field' in kw:
            obj = self.env[kw['model']]
            fname = self.memcached_get_model_time_field(obj)
            if fname:
                times.append((obj.search_read([('id', '=', kw['id'])], [fname]) or [{fname: ''}])[0][fname] or '')
        # Get the latest time of all the parts that build this image and use as the timestamp.
        res['time'] = times and max(times) or ''
        return res
        
class CachedImageMagick(website_imagemagic):
    
    # Getting access errors when I log in to these, but I think that's dependant on the attachment that's used.
    # /imagemagick/209780/id/1                                          # Looks like this skips the recipe entirely?
    # /imagemagick/209780/ref/website_imagemagick.im_carousel_img       # This crashes in website_imagemagick
    
    #~ @http.route(['/imagemagick/<model("ir.attachment"):image>/id/<model("image.recipe"):recipe>',
                 #~ '/imagemagick/<model("ir.attachment"):image>/ref/<string:recipe_id>'], type='http', auth="public", website=True)
    @memcached.route(
        flush_type=lambda kw: 'imagemagick %s' % request.website.get_kw_imagemagick(kw),
        key=lambda kw: '{{db}},/imagemagick/{attachment_id}/id/{recipe_id},{{lang}},{{device_type}} {time}'.format(**request.website.memcached_get_key_imagemagick(kw)),
        binary=True,
        max_age=31536000,
        s_maxage=60*60*24*30,
        cache_age=60*60*24*30
    )
    def view_attachment(self, image=None, recipe=None, recipe_ref=None, **post):
        return super(CachedImageMagick, self).view_attachment(image, recipe, recipe_ref, **post)
    
    # Works 2019-08-28
    # /imageurl/id/1?url=%2Fwebsite%2Fstatic%2Fsrc%2Fimg%2Fvolcano.jpg
    # /imageurl/ref/website_imagemagick.im_carousel_img?url=%2Fwebsite%2Fstatic%2Fsrc%2Fimg%2Fvolcano.jpg
    
    # ~ @http.route([
        # ~ '/imageurl/id/<model("image.recipe"):recipe>',
        # ~ '/imageurl/ref/<string:recipe_ref>'
        # ~ ], type='http', auth="public", website=True)
    @memcached.route(
        flush_type=lambda kw: 'imagemagick %s' % request.website.get_kw_imagemagick(kw),
        key=lambda kw: '{{db}},/imageurl/{url}/id/{recipe_id},{{lang}},{{device_type}} {time}'.format(**request.website.memcached_get_key_imagemagick(kw)),
        binary=True,
        max_age=31536000,
        s_maxage=60*60*24*30,
        cache_age=60*60*24*30
    )
    def view_url(self, recipe=None, recipe_ref=None, **post):
        return super(CachedImageMagick, self).view_url(recipe, recipe_ref, **post)
    
    # Works 2019-08-28
    # /imagefield/ir.attachment/datas/209780/id/1
    # /imagefield/ir.attachment/datas/209780/ref/website_imagemagick.im_carousel_img
    
    #~ @http.route([
        #~ '/imagefield/<model>/<field>/<id>/ref/<recipe_ref>',
        #~ '/imagefield/<model>/<field>/<id>/id/<model("image.recipe"):recipe>',
        #~ ], type='http', auth="public", website=True, multilang=False)
    @memcached.route(
        flush_type=lambda kw: 'imagemagick %s' % request.website.get_kw_imagemagick(kw),
        key=lambda kw: '{{db}},/imagefield/{model}/{field}/{id}/id/{recipe_id},{{lang}},{{device_type}} {time}'.format(**request.website.memcached_get_key_imagemagick(kw)),
        binary=True,
        max_age=31536000,
        s_maxage=60*60*24*30,
        cache_age=60*60*24*30
    )
    def website_image(self, model, id, field, recipe=None, recipe_ref=None, **post):
        return super(CachedImageMagick, self).website_image(model, id, field, recipe, recipe_ref, **post)
    
    # No idea what the point of this address is.
    # /imagefieldurl/ir.attachment/datas/209780/id/1
    # /imagefieldurl/ir.attachment/datas/209780/ref/website_imagemagick.im_carousel_img
    
    #~ @http.route([
        #~ '/imagefieldurl/<model>/<field>/<id>/ref/<recipe_ref>',
        #~ '/imagefieldurl/<model>/<field>/<id>/id/<model("image.recipe"):recipe>',
        #~ ], type='http', auth="public", website=True, multilang=False)
    @memcached.route(
        flush_type=lambda kw: 'imagemagick %s' % request.website.get_kw_imagemagick(kw),
        key=lambda kw: '{{db}},/imagefieldurl/{model}/{field}/{id}/id/{recipe_id}?url={url},{{lang}},{{device_type}} {time}'.format(**request.website.memcached_get_key_imagemagick(kw)),
        binary=True,
        max_age=31536000,
        s_maxage=60*60*24*30,
        cache_age=60*60*24*30
    )
    def website_url(self, model, id, field, recipe=None,recipe_ref=None, **post):
        return super(CachedImageMagick, self).website_url(model, id, field, recipe,recipe_ref, **post)
    
    # Works 2019-08-28
    # /website/imagemagick/ir.attachment/datas/209780/1
    
    #~ @http.route([
        #~ '/website/imagemagick/<model>/<field>/<id>/<model("image.recipe"):recipe>',
        #~ ], type='http', auth="public", website=True, multilang=False)
    @memcached.route(
        flush_type=lambda kw: 'imagemagick %s' %request.website.get_kw_imagemagick(kw),
        key=lambda kw: '{{db}},/website/imagemagick/{model}/{field}/{id}/{recipe_id},{{lang}},{{device_type}} {time}'.format(**request.website.memcached_get_key_imagemagick(kw)),
        binary=True,
        max_age=31536000,
        s_maxage=60*60*24*30,
        cache_age=60*60*24*30
    )
    def website_imagemagick(self, model, field, id, recipe=None, **post):
        return super(CachedImageMagick, self).website_imagemagick(model, field, id, recipe, **post)
    
    # Works 2019-08-28
    # /imagefield/ir.attachment/datas/209780/ref/website_imagemagick.im_carousel_img/image/foobar.jpeg
    
    # '/imagefield/<model>/<field>/<id>/ref/<recipe_ref>/image/<file_name>'
    @memcached.route(
        flush_type=lambda kw: 'imagemagick',
        # ~ key=lambda kw: '{{db}},/imagefield/{model}/{field}/{id}/ref/{recipe_id}/image/{file_name},{{lang}},{{device_type}} {time}'.format(**request.website.memcached_get_key_imagemagick(kw)),
        no_cache=False,
        must_revalidate=False,
        proxy_revalidate=False,
        binary=True,
        max_age=31536000,
        s_maxage=60*60*24*30,
        cache_age=60*60*24*30
    )
    def website_image_hash(self, model, id, field, recipe_ref, file_name=None, **post):
        return super(CachedImageMagick, self).website_image_hash(model, id, field, recipe_ref, **post)
