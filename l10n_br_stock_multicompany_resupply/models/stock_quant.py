# -*- coding: utf-8 -*-
# Copyright 2016 KMEE - www.kmee.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class StockQuant(models.Model):

    _inherit = "stock.quant"

    @api.model
    def _quants_get_order(self, location, product, quantity, domain=(),
                          orderby='in_date'):
        """
        Fix quant visibility to match the location instead of the user company
        """
        # This is necessary while the PR below is not merged:
        # https://github.com/odoo/odoo/pull/16189
        if location and 'force_company' not in self.env.context:
            if location.company_id.id:
                self = self.with_context(force_company=location.company_id.id)
        return super(StockQuant, self)._quants_get_order(
            location, product, quantity, domain=domain, orderby=orderby)
