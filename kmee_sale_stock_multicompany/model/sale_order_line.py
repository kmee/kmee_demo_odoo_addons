# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, models, api, fields


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
