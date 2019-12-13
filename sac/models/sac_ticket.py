# Copyright 2019 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class SacTicket(models.Model):

    _name = 'sac.ticket'
    _description = 'Sac Ticket'  # TODO

    name = fields.Char()
