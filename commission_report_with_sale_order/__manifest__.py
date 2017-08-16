# -*- coding: utf-8 -*-
##############################################################################
#
#    Commission Update Wizard
#    Copyright (C) 2016 KMEE (http://www.kmee.com.br)
#    @author Daniel Sadamo <daniel.sadamo@kmee.com.br>
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
##############################################################################

{
    'name': 'Commission Report With Sale Order',
    'license': 'AGPL-3',
    'author': 'KMEE',
    'version': '8.0.1.0.0',
    'website': 'http://www.kmee.com.br',
    'depends': [
        'sale_commission',
        'account_invoice_sale_link',
    ],
    'data': [
        'report/settlements_report.xml'
    ],
    'test': [
    ],
    'category': 'Report',
    'installable': False,

}
