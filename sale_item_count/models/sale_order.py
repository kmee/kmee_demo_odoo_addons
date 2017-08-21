# -*- coding: utf-8 -*-
# © <2016> <Luis Felipe Mileo>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line')
    @api.multi
    def _count_quantity(self):
        for order in self:
            total = 0.0
            for line in order.order_line:
                total += line.product_uom_qty
            order.total_items = total

    total_items = fields.Float(
        string="Qtde Total",
        digits=dp.get_precision('Product UoS'),
        compute='_count_quantity',
        copy=False,
    )


class SaleOrdeLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _default_line(self):
        if self.env.context.get('ref_ids'):
            return len(self.env.context['ref_ids']) + 1
        else:
            return 1

    @api.multi
    def _get_line_numbers(self):
        index = 1
        for line in self[0].order_id.order_line:
            line.line_number = index
            index += 1

    line_number = fields.Integer(string="Item",
                                 compute='_get_line_numbers',
                                 default=_default_line,
                                 copy=False)
