# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	pdc_account_id = fields.Many2one('account.account',string="PDC Receivable Account", related='company_id.pdc_account_id', readonly=False)
	pdc_account_creditors_id = fields.Many2one('account.account',string="PDC Payable Account", related='company_id.pdc_account_creditors_id', readonly=False)

