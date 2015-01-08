# -*- coding: utf-8 -*-
##############################################################################
#
#    KMEE, KM Enterprising Engineering
#    Copyright (C) 2013 - Luis Felipe Miléo (<http://www.kmee.com.br>).
#
#    This program is free software: you can redistribute it and    /or modify
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
##############################################################################

{
    'name': 'Mobile Sales Management',
    'version': '0.1',
    'category': 'Sales Mobile Integration With Apogeus',
    'sequence': 14,
    'summary': 'Mobile Sales Orders',
    'description': """

    """,
    'author': 'KMEE',
    'website': 'http://www.kmee.com.br',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
