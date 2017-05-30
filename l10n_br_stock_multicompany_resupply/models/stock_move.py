# -*- coding: utf-8 -*-
# Copyright 2016 KMEE - www.kmee.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.multi
    def action_done(self):
        """ Chamando o metodo como super para não desabilitar a regra de
        segurança e do stock.move (ação que causa problemas na quantidade de
        estoques das filiais)
        """
        return super(StockMove, self.sudo()).action_done()

    @api.model
    def split(self, move, qty, restrict_lot_id=False,
              restrict_partner_id=False):
        return super(StockMove, self.sudo()).split(
            move, qty, restrict_lot_id=restrict_lot_id,
            restrict_partner_id=restrict_partner_id
        )
