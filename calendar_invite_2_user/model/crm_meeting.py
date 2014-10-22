# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 KMEE (http://www.kmee.com.br)
#    @author Luis Felipe Mileo <mileo@kmee.com.br>
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

from osv import fields, orm

class CrmMeeting(orm.Model):
    """ Sale Order Stock"""
    _inherit = "crm.meeting" 

    def _get_default_partner(self, cr, uid, context=None):
        res = []
        res.append(self.pool.get('res.users').browse(cr, uid, uid, context).partner_id.id)
        return res
    
    _defaults = {
        'partner_ids':  lambda self, cr, uid, ctx=None: self._get_default_partner(cr, uid, context=ctx),
    }