# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Hr Expense Document Attachment Preview | Image Viewer, Image Preview (jpg/jpeg/png/gif) | PDF Viewer,PDF Preview | Attachment Viewer',
    'version': '14.0.1',
    'category': 'Generic Modules/Human Resources',
    'sequence': 1,
    'summary': 'Document Preview',
    'description': """
    This module shows preview of document like PDF & Image(jpg/jpeg/png/gif) from expense lines.
    """,
    'author' : 'GYB IT SOLUTIONS',
    'website': 'https://www.gybitsolutions.com',
    'license': 'AGPL-3',
    'depends': ['web', 'hr_expense'],
    'data': [
        'views/hr_template.xml',
        'views/hr_expense.xml',
    ],
    'images': ['static/description/banner.png',],
    'currency':'USD',
    'price': 18.0,
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
