# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import re
import json


class WizardRegisterNumber(models.TransientModel):
    _name = 'wizard.register.number'
    _description = _('Registering a new TotalVoice Number')

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact',
        readonly=True,
    )

    @api.model
    def _get_numbers(self):
        selection_numbers = []
        partner_id = self.partner_id or self.env['res.partner'].browse(
            self.env.context.get('default_partner_id'))
        if partner_id.mobile:
            mobile = re.sub('\D', '', partner_id.mobile or '')
            selection_numbers.append((mobile,
                                      _('Mobile: ') + partner_id.mobile))

        if partner_id.phone:
            phone = re.sub('\D', '', partner_id.phone or '')
            selection_numbers.append((phone, _('Phone: ') + partner_id.phone))

        return selection_numbers

    number = fields.Selection(
        selection='_get_numbers',
        string='Number',
        help='Select a Number',
    )

    server_message = fields.Char(
        string='Server Message',
        readonly=True,
        size=160,
    )

    activation_code = fields.Char(
        string='Activation Code',
        size=5,
    )

    @api.multi
    def action_already_registered(self):
        """
        This method update the totalvoice_number from the res_partner with
        the number selected and adds the res_partner to the
        api_registered_partner_ids at the totalvoice_odoo config
        """
        totalvoice_api = self.env['totalvoice.api.config']

        self.server_message = _('Number already registered')
        totalvoice_api.register_partner(self.partner_id, self.number)

        return True

    @api.multi
    def action_register_number(self):
        """
        Registers the contact's number in the TotalVoice System.
        :return: True if the number is already registered. Else if it's not
        """
        totalvoice_api = self.env['totalvoice.api.config']

        already_registered = totalvoice_api.\
            verify_registered_number(self.number)

        if already_registered:
            return self.action_already_registered()
        else:
            totalvoice_api.get_client().bina.enviar(self.number)
            self.server_message = _('Code sent')

        return {
            "type": "ir.actions.do_nothing",
        }

    @api.multi
    def action_confirm_number_code(self):

        if not self.activation_code:
            raise ValidationError(_("Activation Code must be filled"))

        totalvoice_api = self.env['totalvoice.api.config']

        already_registered = \
            totalvoice_api.verify_registered_number(self.number)

        if already_registered:
            return self.action_already_registered()
        else:
            bina_report = json.loads(totalvoice_api.get_client().bina.\
                validar(self.activation_code, self.number))

            if bina_report.get('sucesso'):
                if not totalvoice_api.verify_registered_number(self.number):
                    self.server_message = _("The number could not be "
                                            "registered. Probably due a "
                                            "invalid verification code")
                else:
                    self.server_message = _('Number Successfully Registered')
            else:
                self.server_message = _('Error ') + ' ' + \
                                      str(bina_report.get('motivo')) + ' - ' \
                                      + bina_report.get('mensagem')

        totalvoice_api.register_partner(self.partner_id, self.number)

        return {
            "type": "ir.actions.do_nothing",
        }
