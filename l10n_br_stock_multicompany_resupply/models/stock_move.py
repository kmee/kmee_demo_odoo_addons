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
