# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _


class product_product(osv.osv):

    _inherit = 'product.product'
    _columns = {
        'create_date': fields.datetime('Date Created', readonly=True),
        'write_date': fields.datetime('Date Alteracao', readonly=True)
#     'last_write': fields.datetime('Date Ultima Alteracao', readonly=True)
    }


#class product_pricelist(osv.osv):

    #_inherit = 'product.pricelist'
    #_columns = { 'user_id': fields.many2one('res.users', 'User',
        #help="The user responsible for this journal")
        #}

        #'taxes_id': fields.many2many('account.tax', 'product_taxes_rel',
            #'prod_id', 'tax_id', 'Customer Taxes',
            #domain=[('parent_id','=',False),('type_tax_use','in',['sale','all'])]),

    #TODO: situação do registro, alterado, excluido, incluido etc.
    #no test: def write (self, cr, uid, values, context=None):
        #values.update({'last_write': values.get('write_date')})
        #res = super('product_product',self).create(cr,uid,values,
            #context=context)
        #return res