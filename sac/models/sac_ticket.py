# Copyright 2019 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class SacTicket(models.Model):

    _name = 'sac.ticket'
    _description = 'Sac Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        default=lambda self: _('New'),
    )
    assunto_id = fields.Many2one(
        'sac.assunto',
    )

    partner_id = fields.Many2one('res.partner')
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
    partner_email = fields.Char()
    partner_zip = fields.Char()
    partner_street = fields.Char()
    partner_street2 = fields.Char()
    partner_district = fields.Char()
    partner_state_id = fields.Many2one(
        comodel_name='res.country.state',
        domain=[('country_id.code', '=', 'BR')]
    )
    partner_city = fields.Char()
    mensagem = fields.Text()

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.partner_name = self.partner_id.name
            self.partner_phone = self.partner_id.phone
            self.partner_email = self.partner_id.email
            self.partner_street = self.partner_id.street
            self.partner_street2 = self.partner_id.street2
            self.partner_zip = self.partner_id.zip
            self.partner_state_id = self.partner_id.state_id
            self.partner_city = self.partner_id.city

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sac') or _('New')
        result = super(SacTicket, self).create(vals)
        return result
