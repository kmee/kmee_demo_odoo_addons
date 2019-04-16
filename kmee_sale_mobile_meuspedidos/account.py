# -*- coding: utf-8 -*-
##############################################################################
#
#    KMEE, KM Enterprising Engineering
#    Copyright (C) 2013 - Luis Felipe Miléo (<http://www.kmee.com.br>).
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
from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_payment_term(osv.osv):
    _inherit = 'account.payment.term'
    _columns = {
        'mobile': fields.boolean('Mobile', help="If the active payment term is active in mobile sales")
    }
    _defaults = {
        'mobile': 1,
    }