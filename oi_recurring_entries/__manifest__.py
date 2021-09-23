# -*- coding: utf-8 -*-
##############################################################################

{
    'name': 'Recurring Entries',
    "summary": 'Recurring Entries, Recurring, Automatic, Periodic, Auto Recurring, Repeat, Auto Repeat',
    'version': '14.0.1.1.6',
    'author': 'Openinside',
    'website': "https://www.open-inside.com",
    'category': 'Accounting',
    'description': """
        
    """,
    
    'depends' : ['account', 'oi_base'],
    'data': [        
        'view/recurring_entry.xml',
        'view/recurring_entry_line.xml',
        'view/account_move.xml',
        'view/action.xml',
        'view/menu.xml',
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
    ],
    'images':[
        'static/description/cover.png'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    "license": "OPL-1",
    "price" : 70,
    "currency": 'EUR',
    'odoo-apps' : True              
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
