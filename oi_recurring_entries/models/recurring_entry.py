'''
Created on Apr 1, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from odoo.osv.expression import FALSE_DOMAIN

from dateutil.rrule import rrule, MONTHLY

class RecurringEntry(models.Model):
    _name = 'recurring.entry'
    _description = 'Recurring Entry'
    #_inherit = 'account.move'
    _rec_name='ref'
    
    
    @api.model
    def _search_default_journal(self, journal_types):
        company_id = self._context.get('default_company_id', self.env.company.id)
        domain = [('company_id', '=', company_id), ('type', 'in', journal_types)]

        journal = None
        if self._context.get('default_currency_id'):
            currency_domain = domain + [('currency_id', '=', self._context['default_currency_id'])]
            journal = self.env['account.journal'].search(currency_domain, limit=1)

        if not journal:
            journal = self.env['account.journal'].search(domain, limit=1)

        if not journal:
            company = self.env['res.company'].browse(company_id)

            error_msg = _(
                "No journal could be found in company %(company_name)s for any of those types: %(journal_types)s",
                company_name=company.display_name,
                journal_types=', '.join(journal_types),
            )
            raise UserError(error_msg)

        return journal
    
    @api.model
    def _get_default_journal(self):
        ''' Get the default journal.
        It could either be passed through the context using the 'default_journal_id' key containing its id,
        either be determined by the default type.
        '''
        move_type = self._context.get('default_move_type', 'entry')
        if move_type in self.get_sale_types(include_receipts=True):
            journal_types = ['sale']
        elif move_type in self.get_purchase_types(include_receipts=True):
            journal_types = ['purchase']
        else:
            journal_types = self._context.get('default_move_journal_types', ['general'])

        if self._context.get('default_journal_id'):
            journal = self.env['account.journal'].browse(self._context['default_journal_id'])

            if move_type != 'entry' and journal.type not in journal_types:
                raise UserError(_(
                    "Cannot create an invoice of type %(move_type)s with a journal having %(journal_type)s as type.",
                    move_type=move_type,
                    journal_type=journal.type,
                ))
        else:
            journal = self._search_default_journal(journal_types)

        return journal

    @api.model
    def _get_default_currency(self):
        ''' Get the default currency from either the journal, either the default journal's company. '''
        journal = self._get_default_journal()
        return journal.currency_id or journal.company_id.currency_id

    
    
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        check_company=True, domain="[('id', 'in', suitable_journal_ids)]",
        default=_get_default_journal)
    
    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                 store=True, readonly=True,
                                 compute='_compute_company_id')

    currency_id = fields.Many2one('res.currency', store=True, readonly=True, tracking=True, required=True,
        states={'draft': [('readonly', False)]},
        string='Currency',
        default=_get_default_currency)
    
    narration = fields.Text(string='Terms and Conditions')
    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')
    
    partner_id = fields.Many2one('res.partner', readonly=True, tracking=True,
        states={'draft': [('readonly', False)]},
        check_company=True,
        string='Partner', change_default=True)
    
    @api.model
    def _get_date(self):
        return fields.Date.today() + relativedelta(day=31)
    
    
    @api.model
    def get_sale_types(self, include_receipts=False):
        return ['out_invoice', 'out_refund'] + (include_receipts and ['out_receipt'] or [])

    @api.model
    def get_purchase_types(self, include_receipts=False):
        return ['in_invoice', 'in_refund'] + (include_receipts and ['in_receipt'] or [])


    recurring_state = fields.Selection([('draft', 'Draft'), ('running', 'Running'), ('closed','Closed')], required = True, default = 'draft', string='Recurring Status', copy = False)
    
    line_ids = fields.One2many('recurring.entry.line', 'move_id', copy = True)
    
    date = fields.Date(string='Start Date', default = _get_date)
    date_end = fields.Date(string='End Date' , copy = False)
    
    move_ids = fields.One2many('account.move', 'recurring_id')
        
    entries_count = fields.Integer(compute= '_calc_entries_count')
    
    ref = fields.Char(required=True, copy = True)
    
    recurring_type = fields.Selection([('post', 'Automatic (Post)'), ('draft', 'Automatic (Draft)'), ('manual', 'Manually')], string='Recurring Type', required = True, default = 'post', copy = False)
    
    method_period = fields.Integer(
        string='Period Length',
        default=1,
        help="State here the time between 2 entries, in months",
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    
    #journal_id = fields.Many2one('account.journal',  readonly = True)
    
    transaction_ids = fields.Many2many('recurring.entry', store = False, domain = FALSE_DOMAIN)
    authorized_transaction_ids = fields.Many2many('recurring.entry', store = False, domain = FALSE_DOMAIN)
    
    
    @api.depends('journal_id')
    def _compute_company_id(self):
        for move in self:
            move.company_id = move.journal_id.company_id or move.company_id or self.env.company


    @api.depends('ref')
    def _compute_name(self):
        for record in self:
            record.name = record.ref
    
    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        pass
    
    
    def name_get(self):
        return self._base().name_get(self)
    
    def action_confirm(self):
        self.write({'recurring_state' : 'running'})
        
    def action_close(self):
        self.write({'recurring_state' : 'closed'})        
        
    def action_draft(self):
        self.write({'recurring_state' : 'draft'})     
    
    def action_create(self): 
        if self.recurring_type !='manual':
            self._auto_create_entries()
            return
        
        data = self.copy_data({'date' : fields.Date.today(),
                               'recurring_id' : self.id
                               })[0]
        for key in list(data):
            if key not in self.env['account.move']:
                data.pop(key)
        
        for _,_, line_vals in data.get('line_ids'):
            for name in list(line_vals):
                if name not in self.env['account.move.line'] or name in ['move_id']:
                    line_vals.pop(name)
                
        self.env['account.move'].create(data)     
        return self.open_entries()
        
    def open_entries(self):
        action = self.env.ref('account.action_move_journal_line').read()[0]
        action['domain']=[('recurring_id','in', self.ids)]
        action['context']={}
        return action
    
    @api.depends('move_ids')
    def _calc_entries_count(self):
        res = self.env['account.move'].read_group([('recurring_id','in', self.ids)],['recurring_id'],['recurring_id'])
        res = {record['recurring_id'][0] : record['recurring_id_count'] for record in res}
        for record in self:
            record.entries_count = res.get(record.id)
            
    @api.constrains('line_ids')
    def assert_balanced(self):
        if not self.ids:
            return True
        prec = self.env['decimal.precision'].precision_get('Account')

        self._cr.execute("""\
            SELECT      move_id
            FROM        recurring_entry_line
            WHERE       move_id in %s
            GROUP BY    move_id
            HAVING      abs(sum(debit) - sum(credit)) > %s
            """, (tuple(self.ids), 10 ** (-max(5, prec))))
        if len(self._cr.fetchall()) != 0:
            raise UserError(_("Cannot create unbalanced journal entry."))
        return True
    
    @api.constrains('date','date_end')
    def _check_date(self):         
        for record in self:
            if record.date_end and record.date_end < record.date:
                raise ValidationError('End Date < Start Date')
    
    @api.constrains('method_period')
    def _check_method_period(self):
        for record in self:
            if record.method_period <=0:
                raise ValidationError('Invalid Period Length')
                
    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):
        return self._base().create(self,vals_list)
       
    def write(self,vals):
        return self._base().write(self,vals)
    
    def unlink(self):
        return self._base().unlink(self)    
    
    def _auto_create_entries(self):
        today = fields.Date.today()
        for record in self:
            bymonthday = None
            if record.date.day > 27:
                bymonthday = -1
                
            date_end = today if not record.date_end else min(record.date_end, today)
                
            for dt in rrule(MONTHLY, record.date, until=date_end, interval = record.method_period, bymonthday=bymonthday):
                dt = dt.date()
                if self.env['account.move'].search([('recurring_id','=', record.id), ('date','=', dt)], count = True):
                    continue                
                
                vals = record.copy_data({'date' : dt, 'recurring_id' : record.id})[0]
                
                for name in list(vals):
                    if name not in self.env['account.move']:
                        vals.pop(name)
                        
                for _,_, line_vals in vals.get('line_ids', []):
                    for name in list(line_vals):
                        if name not in self.env['account.move.line'] or name in ['move_id']:
                            line_vals.pop(name)                        
                
                move = self.env['account.move'].create(vals)
                if record.recurring_type=='post':
                    move.post()
                
            if record.date_end and record.date_end < today:
                record.recurring_state='closed'                    
            
    @api.model
    def _cron_create_entries(self):
        today = fields.Date.today()
        records = self.search([('recurring_state','=', 'running'),('recurring_type','!=', 'manual'), ('date', '<=', today)])
        records._auto_create_entries()
