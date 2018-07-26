# -*- coding: utf-8 -*-
# Copyright 2018 KMEE INFORMATICA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'NFe Emissão Manual',
    'description': """""",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE INFORMATICA',
    'website': 'www.kmee.com.br',
    'depends': [
        'l10n_br_account_product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/importar_nfe_wizard.xml',
    ],
    'demo': [
    ],
}
