# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields,api,_


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    #@api.multi
    def prev(self):
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
