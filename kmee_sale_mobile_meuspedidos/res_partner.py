# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _


class res_partner(osv.osv):

    _inherit = 'res.partner'
    _columns = {
        'create_date': fields.datetime('Date Created', readonly=True),
        'write_date': fields.datetime('Date Alteracao', readonly=True)
    }