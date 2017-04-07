# -*- coding: utf-8 -*-
# Copyright 2016 KMEE - www.kmee.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.multi
    def action_done(self):
        """ Chamando o metodo como super quando o movimento tiver um movimento
        encadeado em outra empresa, para não desabilidar a regra de segurança
        e do stock.move ( ação que causa problemas na quantidade de estoques
        das filiais)
        """
        for move in self:
            if move.company_id.id != move.location_dest_id.company_id.id:
                return super(StockMove, move.sudo()).action_done()
            return super(StockMove, move).action_done()

    @api.multi
    def action_assign(self):
        """ Execução como sudo para permitir acesso ao armazém da empresa
        que enviou a mercadoria, permitindo que a disponibilidade do material
        que já foi movimentado de estoque para intercompany seja acessada.
        :return:
        """
        for move in self:
            if move.company_id.id != move.location_dest_id.company_id.id:
                return super(
                    StockMove, move.sudo().with_context(
                        force_company=move.sudo().warehouse_id.company_id.id
                    )
                ).action_assign()
            return super(
                StockMove, move
            ).action_assign()
