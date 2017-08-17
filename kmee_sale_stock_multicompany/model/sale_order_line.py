# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from __future__ import division, print_function, unicode_literals

from odoo import SUPERUSER_ID, models, api, fields


class SaleOrderLine(models.Model):

    _inherit = b'sale.order.line'

    stock_line_id = fields.One2many(
        comodel_name='product.stock_multicompany',
        inverse_name='line_id',
        string='Order Lines',
        readonly=True,
    )

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):

        result_super = super(SaleOrderLine, self).product_id_change()

        # Zerar
        self.stock_line_id = False

        if not self.product_id:
            return result_super

        product_stock = self.env['product.stock_multicompany']
        self.stock_line_id = product_stock.get_stock(self.product_id)
        return result_super
