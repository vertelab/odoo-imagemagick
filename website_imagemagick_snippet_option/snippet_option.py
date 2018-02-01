# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
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
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import models, fields, api, _
from openerp import http
from openerp.http import request
import re
import logging
_logger = logging.getLogger(__name__)


class snippet_option(http.Controller):

    @http.route(['/website_imagemagick_snippet_options'], type='json', auth="public", website=True)
    def website_imagemagick_snippet_options(self, img_src, recipe_id, **kw):
        if '/website/image/ir.attachment/' in img_src:
            attachment_id = re.search('/website/image/ir.attachment/(.*)/datas', img_src).group(1).split('_')[0]
        elif '/imagefield/ir.attachment/datas/' in img_src:
            attachment_id = re.search('/imagefield/ir.attachment/datas/(.*)/id', img_src).group(1)
        else:
            attachment_id = 0
        attachment = request.env['ir.attachment'].browse(int(attachment_id))
        return '/imagefield/ir.attachment/datas/%s/id/%s' %(attachment.id, recipe_id)
