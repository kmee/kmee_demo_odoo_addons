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
        moves_inter_company = self.filtered(
            lambda move:
            move.company_id.id != move.location_dest_id.company_id.id
        )
        moves_in_company = self - moves_inter_company
        for move_inter in moves_inter_company.sudo():
            super(StockMove, move_inter).action_done()
        for move_in in moves_in_company:
            super(StockMove, move_in).action_done()
        return True

    @api.multi
    def action_assign(self):
        """ Execução como sudo para permitir acesso ao armazém da empresa
        que enviou a mercadoria, permitindo que a disponibilidade do material
        que já foi movimentado de estoque para intercompany seja acessada.
        :return:
        """
        moves_inter_company = self.filtered(
            lambda move:
            move.company_id.id != move.location_dest_id.company_id.id
        )
        moves_in_company = self - moves_inter_company
        for move_inter in moves_inter_company.sudo():
            super(
                StockMove, move_inter.with_context(
                    force_company=move_inter.sudo().warehouse_id.company_id.id
                )
            ).action_assign()
        for move_in in moves_in_company:
            super(StockMove, move_in).action_assign()
        return True
