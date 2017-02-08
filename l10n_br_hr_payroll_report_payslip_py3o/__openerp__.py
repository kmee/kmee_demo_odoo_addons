# -*- coding: utf-8 -*-
# Categories can be used to filter modules in modules listing
# github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
{
    'name': "Payslip py3o demo report",

    'summary': """
        bla
    """,

    'description': """
        bla
    """,

    'author': "KMEE",
    'website': "http://www.kmee.com.br",

    'category': 'Tools',
    'version': '0.1',
    'depends': [
        'base',
        'crm',
        'report_py3o',
    ],
    'data': [
        'reports/reports.xml',
    ],
}
