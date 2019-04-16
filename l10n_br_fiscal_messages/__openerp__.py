# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2016 Kmee - www.kmee.com.br
#   @author Luiz Felipe do Divino
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'Brazilian Localization Fiscal Aditional Messages',
    'description': 'Brazilian Localization Fiscal Aditional Messages',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'author': 'KMEE',
    'website': 'http://www.kmee.com.br',
    'version': '8.0.1.0.0',
    'depends': [
        'l10n_br',
        'l10n_br_base',
        'l10n_br_account',
        'l10n_br_account_product',
        'nfe',
    ],
    'data': [
        'views/account_fiscal_position_view.xml',
        'views/invoice_messages_view.xml',
        'views/l10n_br_account_fiscal_category_view.xml',
        'views/res_company_view.xml',
        # 'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}