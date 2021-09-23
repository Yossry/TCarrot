# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import base64
import odoo
from odoo import http
from odoo.http import request


class expense_document(http.Controller):
    @http.route("/preview", type="json", auth="public")
    def get_attachment(self, line_id=None, **kwargs):
        print("\n def get_attachment()====", self, line_id)
        values = []
        Attachment = request.env['ir.attachment']
        attachment_ids = Attachment.sudo().search([('res_model','=','hr.expense'),('res_id','=',line_id)])
        if attachment_ids:
            for attach in attachment_ids:
                values.append({
                    'id': attach.id,
                    'name': str(attach.name)+'.'+attach.mimetype.split("/")[1],
                    'label': str(attach.name) + attach.mimetype.split("/")[1],
                    'url': '/web/content/' + str(attach.id) + '?download=false',
                    'type': 'binary',
                })
        return values

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: