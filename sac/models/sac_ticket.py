# Copyright 2019 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class SacTicket(models.Model):

    _name = 'sac.ticket'
    _description = 'Sac Ticket'  # TODO

    name = fields.Char()

    partner_name = fields.Char()
    partner_gender = fields.Selection(
        selection=[
            ('m', 'Masculino'),
            ('f', 'Feminino'),
        ]
    )
    partner_birthday = fields.Date()
    partner_profession = fields.Char()
    partner_phone = fields.Char()
    partner_zip = fields.Char()
    partner_street = fields.Char()
    partner_street2 = fields.Char()
    partner_district = fields.Char()
    partner_state_id = fields.Many2one(
        comodel_name='res.country.state',
        domain=[('country_id.code', '=', 'BR')]
    )
    partner_city = fields.Char()
