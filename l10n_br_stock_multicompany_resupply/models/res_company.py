# -*- coding: utf-8 -*-
# Copyright 2016 KMEE - www.kmee.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ResCompany(models.Model):

    _inherit = 'res.company'

    stock_out_resupply_fiscal_category_id = fields.Many2one(
        'l10n_br_account.fiscal.category',
        u'Categoria Fiscal Padrão de saída de transferencias entre filiais',
        domain="[('journal_type', 'in', ('purchase_refund', 'sale')),"
               "('fiscal_type', '=', 'product'), ('type', '=', 'output')]")
    stock_out_resupply_invoice_state = fields.Selection(
        selection=[
            ("invoiced", "Invoiced"),
            ("2binvoiced", "To Be Invoiced"),
            ("none", "Not Applicable")
        ],
        string=u"Tipo de faturamento padrão de saída",
        help=u"""Define o tipo de faturamento padrão aplicável nas operaçoes de
        de envio, saindo desta empresa para outra filial"""
    )
    stock_in_resupply_fiscal_category_id = fields.Many2one(
        'l10n_br_account.fiscal.category',
        u'Categoria Fiscal Padrão de entrada de transferencias entre filiais',
        domain="[('journal_type', 'in', ('sale_refund', 'purchase')), "
               "('fiscal_type', '=', 'product'), ('type', '=', 'input')]")
    stock_in_resupply_invoice_state = fields.Selection(
        selection=[
            ("invoiced", "Invoiced"),
            ("2binvoiced", "To Be Invoiced"),
            ("none", "Not Applicable")
        ],
        string=u"Tipo de faturamento padrão de entrada",
        help=u"""Define o tipo de faturamento padrão aplicável nas operaçoes de
        de envio, saindo desta empresa para outra filial"""
    )
