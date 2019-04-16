# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _


class delivery_carrier(osv.osv):

    _inherit = 'delivery.carrier'
    _columns = {
        'create_date': fields.datetime('Date Created', readonly=True),
        'write_date': fields.datetime('Date Alteracao', readonly=True)
    }