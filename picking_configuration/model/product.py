# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2015 Kmee - www.kmee.com.br
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
##############################################################################

from openerp import models, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def get_ean(self, product_id, *args):
        result = [self.ean13, product_id['picking_operation_id']]
        return result
