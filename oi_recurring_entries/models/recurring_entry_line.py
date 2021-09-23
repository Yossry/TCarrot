'''
Created on Apr 1, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields, api
from odoo.osv.expression import FALSE_DOMAIN

class RecurringEntryLine(models.Model):
    _name = 'recurring.entry.line'
    _description = 'Recurring Entry Line'
    #_inherit = 'account.move.line'
    
    account_id = fields.Many2one('account.account', string='Account',
        index=True, ondelete="cascade",
        domain="[('deprecated', '=', False), ('company_id', '=', 'company_id'),('is_off_balance', '=', False)]",
        check_company=True,
        tracking=True)
    company_id = fields.Many2one(related='move_id.company_id', store=True, readonly=True, default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict')
    name = fields.Char(string='Label', tracking=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
        index=True, compute="_compute_analytic_account", store=True, readonly=False, check_company=True, copy=True)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags',
        compute="_compute_analytic_account", store=True, readonly=False, check_company=True, copy=True)
    product_id = fields.Many2one('product.product', string='Product', ondelete='restrict')
    date = fields.Date(related='move_id.date', store=True, readonly=True, index=True, copy=False, group_operator='min')
    amount_currency = fields.Monetary(string='Amount in Currency', store=True, copy=True,
        help="The amount expressed in an optional other currency if it is a multi-currency entry.")
    company_currency_id = fields.Many2one(related='company_id.currency_id', string='Company Currency',
        readonly=True, store=True,
        help='Utility field to express amount currency')
    debit = fields.Monetary(string='Debit', default=0.0, currency_field='company_currency_id')
    credit = fields.Monetary(string='Credit', default=0.0, currency_field='company_currency_id')
    ref = fields.Char(related='move_id.ref', store=True, copy=False, index=True, readonly=False)
    exclude_from_invoice_tab = fields.Boolean(help="Technical field used to exclude some lines from the invoice_line_ids tab in the form view.")
    journal_id = fields.Many2one(related='move_id.journal_id', store=True, index=True, copy=False)

    
    move_id = fields.Many2one('recurring.entry', string='Recurring Entry', ondelete = 'cascade')
    currency_id = fields.Many2one('res.currency', string='Currency', default = lambda self : self.env.company.currency_id)
    
    
    sale_line_ids = fields.Many2many('recurring.entry.line', store = False, domain = FALSE_DOMAIN)
    asset_ids = fields.Many2many('recurring.entry.line', store = False, domain = FALSE_DOMAIN)
    consolidation_journal_line_ids = fields.Many2many('recurring.entry.line', store = False, domain = FALSE_DOMAIN)
    tax_ids = fields.Many2many('account.tax', store = False, domain = FALSE_DOMAIN)
    tax_tag_ids = fields.Many2many('account.account.tag', store = False, domain = FALSE_DOMAIN)
    
    website_id = fields.Many2one('base', store = False, domain = FALSE_DOMAIN)
    asset_id = fields.Many2one('base', store = False, domain = FALSE_DOMAIN)
    
    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):
        return self._base().create(self,vals_list)
        
    def write(self,vals):
        return self._base().write(self,vals)
    
    @api.depends('product_id', 'account_id', 'partner_id', 'date')
    def _compute_analytic_account(self):
        for record in self:
            if not record.exclude_from_invoice_tab or not record.move_id.is_invoice(include_receipts=True):
                rec = self.env['account.analytic.default'].account_get(
                    product_id=record.product_id.id,
                    partner_id=record.partner_id.commercial_partner_id.id or record.move_id.partner_id.commercial_partner_id.id,
                    account_id=record.account_id.id,
                    user_id=record.env.uid,
                    date=record.date,
                    company_id=record.move_id.company_id.id
                )
                if rec:
                    record.analytic_account_id = rec.analytic_id
                    record.analytic_tag_ids = rec.analytic_tag_ids
