# -*- coding: utf-8 -*-
# Copyright (C) 2017 - TODAY Albert De La Fuente - KMEE
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': "Payslip py3o demo report",

    'summary': """
        bla
    """,

    'description': """
        bla
    """,

    'author': "KMEE, Odoo Community Association (OCA)",
    'website': "http://www.kmee.com.br",

    'category': 'Tools',
    'version': '0.1',
    'depends': [
        'base',
        'hr',
        'report_py3o',
    ],
    'data': [
        'wizards/wizard_l10n_br_hr_payroll_analytic_report.xml',
        'reports/reports.xml',
    ],
}
