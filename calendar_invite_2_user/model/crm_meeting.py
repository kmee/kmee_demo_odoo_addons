# -*- coding: utf-8 -*-
# Copyright (C) 2014 KMEE (http://www.kmee.com.br)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class CrmMeeting(models.Model):
    """ Sale Order Stock"""
    _inherit = "crm.meeting"

    partner_ids = fields.Many2many(
        default=lambda self: self.env.user.partner_id.id,
    )
