    # -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 - KMEE- Rafael da Silva Lima (<http://www.kmee.com.br>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name' : 'Kmee Sale Meus Pedidos',
    'version' : '1.0',
    'author' : 'KMEE',
    'description' : 'Módulo para comunicação com API Meus Pedidos',
    'category' : 'Enterprise Innovation',
    'website' : 'http://www.kmee.com.br',
    'depends' : ['l10n_br_sale', 'l10n_br_delivery', 'l10n_br_account_payment'],
    
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'account_view.xml',
        'sale_mobile_view.xml',
        'sale_mobile_admin.xml',
        'data/config_data.xml'
        ],
    'qweb' : [
        "static/src/base.xml",
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}