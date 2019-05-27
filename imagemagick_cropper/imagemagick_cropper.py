# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
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
from odoo import models, fields, api, _
from odoo import http
from odoo.http import request
import base64
from cStringIO import StringIO
try:
    from wand.image import Image
except:
    pass

import logging
_logger = logging.getLogger(__name__)

class imagemagickCropper(http.Controller):

    @http.route(['/imagemagick/cropper', '/imagemagick/<model("ir.attachment"):image>/cropper'], type='http', auth="public", website=True)
    def imagemagick_cropper(self, image=None, **post):
        return request.website.render('imagemagick_cropper.imagemagick_cropper', {'image': image})

    @http.route(['/magick_crop'], type='json', methods=['POST'], website=True)
    def magick_crop(self, name, data, dataX=0, dataY=0, dataWidth=0, dataHeight=0, dataRotate=0, dataScaleX=1, dataScaleY=1, **kw):
        img = request.env['ir.attachment'].create({
            'name': name,
            'type': 'binary',
            'res_model': 'ir.ui.view',
            'datas': data
        })
        #~ if 'ir.attachment' in image_url:
        if img:
            # binary -> decode -> wand.image -> imagemagick -> make_blob() -> encode -> binary
            #~ img_attachment = request.env['ir.attachment'].browse(int(image_url.split('/')[4].split('_')[0]))
            img_attachment = request.env['ir.attachment'].browse(img.id)
            wand_img = Image(blob=getattr(img_attachment, 'datas').decode('base64'))
            try:
                wand_img.crop(int(dataX), int(dataY), width=int(dataWidth), height=int(dataHeight))
                if dataScaleX and dataScaleY:
                    wand_img.resize(int(wand_img.width * float(dataScaleX)), int(wand_img.height * float(dataScaleY)))
                if dataRotate:
                    wand_img.rotate(int(dataRotate))
                img_attachment.write({ 'datas': wand_img.make_blob().encode('base64') })
            except Exception as e:
                return ': '.join(e)
            return 'Magic Crop Completed!'
        else:
            return 'Please using attachment as image!'
