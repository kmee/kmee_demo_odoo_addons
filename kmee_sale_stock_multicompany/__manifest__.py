# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name' : 'KMEE Sale Stock Multi Company',
    'summary' : """
        KMEE Sale Stock Multi Company""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE,Odoo Community Association (OCA)',
    'website' : 'http://www.kmee.com.br',
    'depends' : [
        'sale',
    ],
    'data': [
        'view/sale_order_view.xml',
    ],
    'installable': True,
}