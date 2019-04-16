# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _


class product_product(osv.osv):

    _inherit = 'product.product'
    _columns = {
        'create_date': fields.datetime('Date Created', readonly=True),
        'write_date': fields.datetime('Date Alteracao', readonly=True)
    }