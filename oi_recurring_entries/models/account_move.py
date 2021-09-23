'''
Created on Apr 1, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    recurring_id = fields.Many2one('recurring.entry', string='Recurring Entry', readonly = True, ondelete = 'set null')
    