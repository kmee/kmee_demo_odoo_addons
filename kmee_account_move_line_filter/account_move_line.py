# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2014  KMEE  - www.kmee.com.br - Luis Felipe Mileo             #
#                                                                             #
#This program is free software: you can redistribute it and/or modify         #
#it under the terms of the GNU Affero General Public License as published by  #
#the Free Software Foundation, either version 3 of the License, or            #
#(at your option) any later version.                                          #
#                                                                             #
#This program is distributed in the hope that it will be useful,              #
#but WITHOUT ANY WARRANTY; without even the implied warranty of               #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
#GNU General Public License for more details.                                 #
#                                                                             #
#You should have received a copy of the GNU General Public License            #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.        #
###############################################################################


from openerp.osv import fields, osv

class account_move_line(osv.osv):

    _inherit = "account.move.line"

    _columns = {
		'date_from':fields.function(lambda *a,**k:{}, method=True, type='date',string="Emissão Inicial"),
		'date_to':fields.function(lambda *a,**k:{}, method=True, type='date',string="Emissão Final"),
		'due_date_from':fields.function(lambda *a,**k:{}, method=True, type='date',string="Vencimento Inicial"),
		'due_date_to':fields.function(lambda *a,**k:{}, method=True, type='date',string="Vencimento Final"),
    }

class account_move_line(osv.osv):

    _inherit = "account.move"

    _columns = {
		'date_from':fields.function(lambda *a,**k:{}, method=True, type='date',string="Emissão Inicial"),
		'date_to':fields.function(lambda *a,**k:{}, method=True, type='date',string="Emissão Final"),
		'due_date_from':fields.function(lambda *a,**k:{}, method=True, type='date',string="Vencimento Inicial"),
		'due_date_to':fields.function(lambda *a,**k:{}, method=True, type='date',string="Vencimento Final"),
    }