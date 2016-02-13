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


class Romaneio(models.Model):
    _name = 'stock.romaneio'

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


class RomaneioLines(models.Model):
    _name = 'stock.romaneio.line'

    stock_romaneio_id = fields.Many2one('sotck.romaneio')
    invoice_number = fields.Char('Numero da fatura')
    cidade_destino = fields.Char('Cidade destino')
    valor_declarado = fields.Float('Valor declarado')
    qtd_volumes = fields.Integer('Quantidade Volumes')
