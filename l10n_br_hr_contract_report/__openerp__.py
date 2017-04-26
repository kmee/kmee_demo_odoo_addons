# -*- coding: utf-8 -*-
# Copyright 2017 KMEE - Hendrix Costa <hendrix.costa@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Reports for l10n_br_hr_payslip',
    'summary': 'Reports for l10n_br_hr_payslip',
    'version': '8.0.1.0.0',
    'category': 'Reports',
    'website': 'http://www.kmee.com.br',
    'author': "KMEE, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    'depends': [
        'l10n_br_hr_payroll',
        'report_py3o',
    ],
    'data': [
        'reports/contract_report.xml',
    ],
    'installable': True,
}
