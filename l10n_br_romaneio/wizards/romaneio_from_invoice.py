# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2016 Kmee - www.kmee.com.br
#   @author Luiz Felipe do Divino
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
###############################################################################

import time

from openerp import api, models, fields


class StockRomaneioFromInvoicesLines(models.Model):

    _name = "stock.romaneio.from.invoice.lines"

    line_ids = fields.Many2many(
        'account.invoice',
        'account_invoice_line_relation',
        'move_id',
        'line_id',
        'Invoices'
    )

    @api.multi
    def populate_statement(self):

        stock_romaneio_line_obj = self.env['stock.romaneio.line']

        for line in self.line_ids:
            invoice_number = line.number
            if line.partner_id.l10n_br_city_id:
                city = line.partner_id.l10n_br_city_id.name
            else:
                city = line.partner_id.city
            volume_quantity = len(line.picking_ids.stock_picking_line)
            invoice_total = line.amount_total

            vals = {
                'invoice_number': invoice_number,
                'cidade_destino': city,
                'valor_declarado': invoice_total,
                'qtd_volumes': volume_quantity,
            }

            stock_romaneio_line_obj.create(vals)

        return {'type': 'ir.actions.act_window_close'}
