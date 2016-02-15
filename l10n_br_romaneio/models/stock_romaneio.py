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

from openerp import api, models, fields


class StockRomaneio(models.Model):
    _name = 'stock.romaneio'

    @api.multi
    def _mount_romaneio_name(self):
        self.name = 'Romaneio - ' + str(self.id) + ' - ' + str(self.data_criacao)

    @api.multi
    @api.depends('stock_romaneio_lines')
    def _get_total_romaneio(self):
        total = len(self.stock_romaneio_lines)
        self.total_value = total

    @api.multi
    @api.depends('stock_romaneio_lines')
    def _get_total_volumes_romaneio(self):
        total = 0

        for line in self.stock_romaneio_lines:
            total += line.qtd_volumes

        self.total_volumes = total

    name = fields.Char(compute='_mount_romaneio_name')
    carrier_id = fields.Many2one('delivery.carrier', 'Transportadoras')
    stock_romaneio_lines = fields.One2many(
        'stock.romaneio.line',
        'stock_romaneio_id',
        'Romaneio lines',
        required=True,
    )
    data_criacao = fields.Datetime(
        'Data Criação',
        readonly=True,
        default=fields.Datetime.now()
    )
    total_value = fields.Integer(
        compute='_get_total_romaneio',
        string='Valor Total',
        store=True,
        readonly=True
    )
    total_volumes = fields.Integer(
        compute='_get_total_volumes_romaneio',
        string='Volumes totais',
        store=True,
        readonly=True
    )


class StockRomaneioLines(models.Model):
    _name = 'stock.romaneio.line'
    _descrition = u'Romaneio de Expediçao'

    @api.multi
    def unlink(self):
        invoice = self.env['account.invoice'].search([
            ('number', '=', self.invoice_number)
        ])
        invoice.write({'stock_romaneio_id': False})
        return super(StockRomaneioLines, self).unlink()

    stock_romaneio_id = fields.Many2one('stock.romaneio')
    invoice_number = fields.Char('Numero da fatura')
    cidade_destino = fields.Char('Cidade destino')
    valor_declarado = fields.Float('Valor declarado')
    qtd_volumes = fields.Integer('Quantidade Volumes')
    invoice_id = fields.One2many(
        comodel_name='account.invoice',
        inverse_name='stock_romaneio_id',
        string='Fatura'
    )

class RomaneioFromInvoice(models.Model):
    _inherit = 'account.invoice'

    stock_romaneio_id = fields.Many2one(
        comodel_name='stock.romaneio',
        string='Romaneio',
        readonly=True
    )
