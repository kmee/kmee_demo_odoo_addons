# -*- encoding: utf-8 -*-
##############################################################################
#
#    KMEE Avoid Quick Create City, State and Country module for OpenERP
#    Copyright (C) 2014 KMEE (http://www.kmee.com.br)
#    @author Matheus Lima Felix <matheus.felix@kmee.com.br>
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
    'name': 'l10n_br_crm Avoid Quick Create City, State and Country',
    'version': '0.1',
    'category': 'Generic Modules',
    'description': """l10n_br_crm Avoid Quick Create City, State and Country""",
    'author': 'KMEE',
    'license': 'AGPL-3',
    'website': 'http://www.kmee.com.br',
    'depends': [
        'web_m2x_options',
        'l10n_br_crm',
    ],
    'data': [
        'view/crm_lead_view.xml',
        ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': True,
}
