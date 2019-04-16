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

from lxml import etree
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

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        line_obj = self.env['account.invoice']
        romaneio = self.env['stock.romaneio'].browse(
            self.env.context['active_id']
        )

        line_ids = line_obj.search([
            ('stock_romaneio_id', '=', False),
            ('state', '=', 'open'),
            ('picking_ids.state', '=', 'done'),
            ('picking_ids.carrier_id.id', '=', romaneio.carrier_id.id)
        ])
        res = super(StockRomaneioFromInvoicesLines, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=False)
        invoices_ids = []
        for line in line_ids:
            invoices_ids.append(line.id)
        domain = '[("id", "in", ' + str(invoices_ids) + ')]'
        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='line_ids']")
        for node in nodes:
            node.set('domain', domain)
        res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def populate_romaneio(self):

        stock_romaneio_line_obj = self.env['stock.romaneio.line']

        romaneio_id = self.env.context['active_id']

        for line in self.line_ids:
            invoice_number = line.number
            city = line.partner_id.zip
            volume_quantity = len(line.picking_ids.stock_picking_line)
            invoice_total = line.amount_total

            vals = {
                'stock_romaneio_id': romaneio_id,
                'invoice_number': invoice_number,
                'cidade_destino': city,
                'valor_declarado': invoice_total,
                'qtd_volumes': volume_quantity,
                'invoice_id': line,
            }
            line.stock_romaneio_id = romaneio_id
            stock_romaneio_line_obj.create(vals)
            # invoice = self.env['account.invoice'].search([('number', '=', invoice_number)])
            # # invoice.write({'stock_romaneio_id': romaneio_id})

        return {'type': 'ir.actions.act_window_close'}
