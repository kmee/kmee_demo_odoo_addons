# -*- coding: utf-8 -*-
# Copyright 2016 KMEE - www.kmee.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'L10n Br Stock Multicompany Resupply',
    'summary': """
        Operacoes de transferencia entre filiais""",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE,Odoo Community Association (OCA)',
    'website': 'www.kmee.com.br',
    'depends': [
        'l10n_br_stock_account'
    ],
    'data': [
        'views/res_company.xml',
        'security/stock_move.xml',
    ],
    'demo': [
    ],
}
