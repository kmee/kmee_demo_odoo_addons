# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, models, api, fields


class ProductStockMultiCompany(models.TransientModel):

    _name = 'product.stock_multicompany'

    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company'
    )

    stock_location = fields.Many2one(
        comodel_name='stock.location',
        string='Localização'
    )

    qty_available = fields.Float(
        string='Quantity On Hand',
        #_product_qty_available, type='float',
    )

    virtual_available = fields.Float(
        string='Quantity Available',
        #_product_virtual_available, type='float',
    )

    line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Order Line Reference',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.multi
    def get_stock(self, product_id):

        result = []
        location_obj = self.env['stock.location']
        locations = location_obj.search(
            [('usage','in', ['internal','supplier'])]
        )

        for location in locations:
            # cria um objeto de product
            product_obj = self.env['product.product']
            # adiciona o location no context
            product_obj = product_obj.with_context(location=location.id)
            # adiciona id do produto procurado no context
            product_obj._ids = [product_id]
            # chama metodo da classe que retorna a disponibilidade no location
            qty = product_obj._product_available()
            # cria instancia para cada location das informacoes de
            # disponibilidade e apenda em um vetor
            product_stock_multicompany_obj = (self.create({
                'product_id': product_id,
                'company_id': location.company_id.id,
                'stock_location': location.id,
                'qty_available': qty[product_id]['qty_available'],
                'virtual_available': qty[product_id]['virtual_available'],
            }))
            result.append(product_stock_multicompany_obj.id)

        # retorna vetor com disponibilidade de determinado produto em todos
        # os locations
        return result
