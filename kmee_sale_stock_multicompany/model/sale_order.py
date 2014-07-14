# -*- encoding: utf-8 -*-
##############################################################################
#
#    Brazillian 5 acts module for OpenERP
#    Copyright (C) 2014 KMEE (http://www.kmee.com.br)
#    @author Luis Felipe Mileo <mileo@kmee.com.br>
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

from osv import fields, orm
from openerp import SUPERUSER_ID

class ProductStockMultiCompany(orm.TransientModel):
    """ Sale Order Stock"""
    _name = "product.stock_multicompany" 

    _columns = {
                'product_id': fields.many2one('product.product', 'Product'),
                'company_id':fields.many2one('res.company','Company'),
                'stock_location':fields.many2one('stock.location','Localização'),
                'qty_available': fields.float(string='Quantity On Hand'), #_product_qty_available, type='float', 
                'virtual_available': fields.float(string='Quantity Available'), #_product_virtual_available, type='float', 
                'line_id': fields.many2one('sale.order.line', 'Order Line Reference', readonly=True, states={'draft':[('readonly',False)]}),
                }

    def get_stock(self, cr, uid, product_id, context):
        
        result = []
        location_obj = self.pool.get('stock.location')
        
        location_ids = location_obj.search(cr, SUPERUSER_ID, [])
        
        for location in location_obj.browse(cr, SUPERUSER_ID, location_ids, context):
            stock = location_obj._product_get_multi_location(cr, SUPERUSER_ID, [location.id], [product_id])
            
            result.append(self.create(cr, uid, {'product_id': product_id,
                                                'company_id': location.company_id.id,
                                                'stock_location': location.id,
                                                'qty_available': stock[product_id],
                                                'virtual_available': stock[product_id],
                                                }, ))
        return result

class SaleOrderLine(orm.Model):
    """ Sale Order """

    _inherit = "sale.order.line"
    _columns = {
                'stock_line_id': fields.one2many('product.stock_multicompany', 'line_id', 'Order Lines', readonly=True),
                }
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='',
                          partner_id=False, lang=False, update_tax=True,
                          date_order=False, packaging=False,
                          fiscal_position=False, flag=False, context=None):
      
        result_super = super(SaleOrderLine, self).product_id_change(
            cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name,
            partner_id, lang, update_tax, date_order, packaging,
            fiscal_position, flag, context)
        
        product_stock = self.pool.get('product.stock_multicompany')
        
        result = {}
        
        if not product:
            return result_super
        
        result['stock_line_id'] = product_stock.get_stock(cr, uid, product, context)        
        result_super['value'].update(result)
        return result_super