# -*- coding: utf-8 -*-

from odoo import models, fields, _


class WizardRegisterNumber(models.TransientModel):
    _name = 'wizard.register.partner.number'
    _description = _('Registering a new TotalVoice Number')

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact',
        readonly=True,
    )

    def register_number(self):
        action = {
            'name': _('Register a New TotalVoice Number'),
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.register.number',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.partner_id and
                                      self.partner_id.id,
            },
        }

        return action
