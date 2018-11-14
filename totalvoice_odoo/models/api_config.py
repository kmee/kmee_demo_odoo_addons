# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from totalvoice.cliente import Cliente

import json
import re

class ApiConfig(models.TransientModel):
    _name = 'totalvoice.api.config'
    _inherit = 'res.config.settings'

    api_key = fields.Char(
        string='API-KEY',
    )
    api_url = fields.Char(
        string='API-URL',
    )

    api_registered_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Registered Contacts (Partners)',
        readonly=True,
    )

    api_balance = fields.Float(
        string='Balance',
        readonly=True,
    )

    @api.model
    def default_get(self, fields):
        res = super(ApiConfig, self).default_get(fields)

        # api_balance
        try:
            res['api_balance'] = json.loads(
                self.get_client().minha_conta
                    .get_saldo()).get('dados').get('saldo')
        except Exception:
            res['api_balance'] = 0

        self.env['ir.config_parameter'].\
            set_param('api_balance', str(res['api_balance']))

        return res

    @api.model
    def get_default_values(self, fields):
        conf = self.env['ir.config_parameter']
        return {
            'api_key': conf.get_param('api_key'),
            'api_url': conf.get_param('api_url'),
            'api_balance': float(conf.get_param('api_balance')),
            'api_registered_partner_ids': json.loads(
                conf.get_param('api_registered_partner_ids') or '[]')
        }

    @api.one
    def set_values(self):
        conf = self.env['ir.config_parameter']
        conf.set_param('api_key', str(self.api_key))
        conf.set_param('api_url', str(self.api_url))
        conf.set_param('api_balance', str(self.api_balance))
        conf.set_param('api_registered_partner_ids',
                       str(self.api_registered_partner_ids.ids))

    def get_client(self, _raise=True):
        """
        :return: The Totalvoice Client Object
        """
        try:
            client = \
                Cliente(self.env['ir.config_parameter'].get_param('api_key'),
                        self.env['ir.config_parameter'].get_param('api_url'),)
        except Exception:
            if _raise:
                raise UserError(_('API-KEY and API-URL not configured'))

        return client

    def number_to_raw(self, number):
        """
        This method cleans an parameter number, removing all its unnecessary
        characters.
        :param number: The string number to be cleaned
        :return: The raw version of the number
        """
        raw_number = re.sub('\D', '', number or '').lstrip('0')
        return raw_number

    def update_registered_partner_numbers(self):
        """
        This method updates the registered partner numbers o2m field, including
        the new numbers that have been added to the TotalVoice Account since
        the last sync.
        Old numbers will be removed.
        Note: If an number is registered but there isn't any partner carrying
        it, a new partner won't be created with this number.
        """
        bina_report = json.loads(self.get_client().bina.get_relatorio())

        # For every number registered in the Totalvoice's system
        for bina in bina_report.get('dados').get('relatorio'):
            phone_number = bina.get('numero_telefone')

            # Checking if the phone_number isn't already in the partner list
            if self.api_registered_partner_ids.filtered(
                    lambda r: r.totalvoice_number == phone_number):
                continue

            # Looking for partners containing the phone_number

            partners = self.env['res.partner'].search(['|',
                                                       ('phone', '!=', False),
                                                       ('mobile', '!=', False)
                                                       ]).filtered(
                lambda r: r.phone and phone_number in [
                    self.number_to_raw(r.phone),
                    self.number_to_raw(r.mobile),
                ]
            )

            for partner in partners:
                # Register the partner as a new totalvoice contact
                self.env['wizard.register.number'].create({
                    'partner_id': partner.id,
                    'number': [(phone_number, phone_number)],
                }).action_register_number()

        return True

    def verify_registered_number(self, number):
        """
        Verifies if the specified number is already registered in
        TotalVoice for the configured account
        :param number: number to be verified
        :return: True if the number is already registered. Else if it's not
        """

        bina_report = json.loads(self.get_client().bina.get_relatorio())

        already_registered = \
            any(number == bina.get('numero_telefone')
                for bina in bina_report.get('dados').get('relatorio'))

        return True if already_registered else False

    def register_partner(self, partner, number):
        """
        Register a new partner in the totalvoice_odoo module configuration
        :param partner: partner to be registered
        """

        already_registered = \
            self.verify_registered_number(number)

        registered_partners = self.env['res.partner'].\
            browse(self.get_default_values(None).
                   get('api_registered_partner_ids'))

        if already_registered:
            if partner.totalvoice_number != number:
                partner.totalvoice_number = number

            if partner not in registered_partners:
                registered_partners += partner
                self.env['ir.config_parameter'].set_param(
                    'api_registered_partner_ids', registered_partners.ids)

    def remove_partner(self, partner):
        """
        Remove res_partner from the api_registered_partner_ids list
        """
        partner.totalvoice_number = False

        registered_partners = self.env['res.partner']. \
            browse(self.get_default_values(None).
                   get('api_registered_partner_ids'))
        registered_partners -= partner
        self.env['ir.config_parameter'].set_param(
            'api_registered_partner_ids', registered_partners.ids)

    def action_register_partner(self):
        action = {
            'name': _('Select contact'),
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.register.partner.number',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('totalvoice_odoo.view_partner_form').id,
            'target': 'new',
            'context': {},
        }

        return action
