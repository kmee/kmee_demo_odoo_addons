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


class InvoiceMessage(models.Model):
    _name = 'invoice.message'
    _rec_name = 'message_invoice'

    def _default_company_id(self):
        company_model = self.env['res.company']
        return company_model._company_default_get(self._name)

    message_invoice = fields.Text('Mensagem')
    company_id = fields.Many2one('res.company', string='Empresa',
                                 default=_default_company_id)
    message_type = fields.Selection([
        ('company', 'Empresa'),
        ('fiscal_position', u'Posição Fiscal'),
        ('fiscal_category', 'Categoria Fiscal')
    ], 'Tipo da mensagem')
    # fiscal_classification_id = fields.Many2many(
    #     'account.product.fiscal.classification',
    #     'invoice_message_fiscal_classification_rel',
    #     'message_id',
    #     'fiscal_classification_id',
    #     string=u'Classificação Fiscal')
    # fiscal_position_id = fields.Many2many(
    #     'account.fiscal.position', 'invoice_message_fiscal_position_rel',
    #     'message_id', 'fiscal_position_id', string=u'Posição Fiscal')
    # company_id = fields.One2many('res.company', u'Empresa')