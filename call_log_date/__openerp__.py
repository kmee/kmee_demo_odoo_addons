# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Fernando Marcato Rodrigues
#    Copyright 2015 KMEE - www.kmee.com.br
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
    'name': 'call_log_date',
    'version': '0.1',
    'category': 'Generic Modules',
    'description': """
        Changes "crm.opportunity2phonecall" wizard view so that the "date"
        field appears for both Schedule and Log Call options.
    """,
    'author': 'KMEE',
    'license': 'AGPL-3',
    'website': '',
    'depends': [
        'crm',
    ],
    'data': [
        'wizard/crm_opportunity_to_phonecall_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
}
