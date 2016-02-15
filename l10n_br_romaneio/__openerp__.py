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
    'name': 'Brazilian Localization Romaneio',
    'description': 'Brazilian Localization Romaneio',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'author': 'KMEE',
    'website': 'http://www.kmee.com.br',
    'version': '8.0.1.0.0',
    'depends': [
        'l10n_br_account_product',
        'delivery',
        'stock_picking_invoice_link',
    ],
    'data': [
        'wizards/stock_romaneio_from_invoice_view.xml',
        'views/account_invoice_view.xml',
        'views/stock_romaneio_views.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}