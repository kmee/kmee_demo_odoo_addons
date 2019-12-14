# Copyright 2019 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class SacAssunto(models.Model):

    _name = 'sac.assunto'
    _description = 'Sac Assunto'  # TODO

    name = fields.Char()
