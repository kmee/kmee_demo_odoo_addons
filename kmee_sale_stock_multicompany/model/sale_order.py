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
from openerp import SUPERUSER_ID, models, api, fields


class ProductStockMultiCompany(models.TransientModel):

    _name = 'product.stock_multicompany'

    product_id = fields.Many2one(
        string = 'Product',
        comodel_name = 'product.product',
    )

    company_id = fields.Many2one(
        comodel_name = 'res.company',
        string = 'Company'
    )

    stock_location = fields.Many2one(
        comodel_name = 'stock.location',
        string = 'Localização'
    )

    qty_available = fields.Float(
        string='Quantity On Hand', #_product_qty_available, type='float',
    )

    virtual_available = fields.Float(
        string='Quantity Available', #_product_virtual_available, type='float',
    )

    line_id = fields.Many2one(
        comodel_name = 'sale.order.line',
        string = 'Order Line Reference',
        readonly=True,
        states={'draft':[('readonly',False)]},
    )

    @api.multi
    def get_stock(self, product_id):

        result = []
        location_obj = self.env['stock.location']
        locations = location_obj.search([('usage','in',['internal','supplier'])])

        for location in locations:
            # cria um objeto de product
            product_obj = self.env['product.product']
            # adiciona o location no context
            product_obj = product_obj.with_context(location= location.id)
            # adiciona id do produto procurado no context
            product_obj._ids = [product_id]
            # chama metodo da classe que retorna a disponibilidade no location
            qty = product_obj._product_available()
            # cria instancia para cada location das informacoes de disponibilidade e apenda em um vetor
            product_stock_multicompany_obj = (self.create({'product_id': product_id, 'company_id': location.company_id.id,
                                                    'stock_location': location.id, 'qty_available': qty[product_id]['qty_available'],
                                                    'virtual_available': qty[product_id]['virtual_available'],}))
            result.append(product_stock_multicompany_obj.id)

        # retorna vetor com disponibilidade de determinado produto em todos os locations
        return result

class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    stock_line_id = fields.One2many(
        comodel_name = 'product.stock_multicompany',
        inverse_name = 'line_id',
        string = 'Order Lines',
        readonly=True,
    )

    @api.multi
    def product_id_change(self, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='',
                          partner_id=False, lang=False, update_tax=True,
                          date_order=False, packaging=False,
                          fiscal_position=False, flag=False):

        result_super = super(SaleOrderLine, self).product_id_change(
            pricelist, product, qty, uom, qty_uos, uos, name,
            partner_id, lang, update_tax, date_order, packaging,
            fiscal_position, flag)

        if not product:
            return result_super

        result = {}
        product_stock = self.env['product.stock_multicompany']
        result['stock_line_id'] = product_stock.get_stock(product)
        result_super['value'].update(result)
        return result_super