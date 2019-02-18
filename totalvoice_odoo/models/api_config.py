# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from totalvoice.cliente import Cliente

from unicodedata import normalize
import json
import re

api_url = 'api.totalvoice.com.br'


class ApiConfig(models.TransientModel):
    _name = 'totalvoice.api.config'
    _inherit = 'res.config.settings'

    api_key = fields.Char(
        string='API-KEY',
    )

    timeout = fields.Integer(
        string='Conversation Time Out (hours)',
        help='The conversation time out for waiting answers (in Hours) !!!',
        default=8,
    )

    archive_timeout = fields.Integer(
        string=_('Conversation archive Time Out (hours)'),
        help=_('The Time Out for archiving DOne Conversations (hours) !!!'),
        default=24,
    )

    api_registered_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Registered Contacts (Partners)',
        readonly=True,
    )

    api_username = fields.Char(
        string='Name',
        readonly=True,
    )

    api_balance = fields.Float(
        string='Balance',
        readonly=True,
    )

    api_login = fields.Char(
        string='Email',
        readonly=True,
    )

    api_phone = fields.Char(
        string='Phone',
        readonly=True,
    )

    api_server_message = fields.Char(
        string='Server Message',
        default='',
        readonly=True,
    )

    api_test_webhook_message = fields.Char(
        string='Webhook Test Message',
        default='010 - Test Message',
    )

    api_test_webhook_id = fields.Char(
        string='Webhook Test ID',
        default='16347',
    )

    api_test_webhook_sms_id = fields.Char(
        string='Webhook Test SMS ID',
        default='133830',
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Partner",
    )

    @api.model
    def default_get(self, fields):
        res = super(ApiConfig, self).default_get(fields)

        # Account Info
        try:
            account_data = json.loads(
                self.get_client().minha_conta.get_conta()
            ).get('dados')

            res['api_username'] = account_data.get('nome')
            res['api_balance'] = account_data.get('saldo')
            res['api_login'] = account_data.get('login')
            res['api_phone'] = account_data.get('telefone')
        except Exception:
            res['api_username'] = ''
            res['api_balance'] = 0
            res['api_login'] = ''
            res['api_phone'] = ''

        self.env['ir.config_parameter'].\
            set_param('api_username',
                      (normalize('NFKD',
                                 unicode(self.api_username or '')).
                       encode('ASCII', 'ignore')))

        self.env['ir.config_parameter']. \
            set_param('api_balance', str(res['api_balance']))
        self.env['ir.config_parameter']. \
            set_param('api_login', str(res['api_login']))
        self.env['ir.config_parameter']. \
            set_param('api_phone', str(res['api_phone']))

        updated_res_partner_ids = self.update_registered_partner_numbers()

        if updated_res_partner_ids:

            res['api_registered_partner_ids'] = updated_res_partner_ids.ids

            self.env['ir.config_parameter'].set_param(
                'api_registered_partner_ids',
                str(res['api_registered_partner_ids']))

        return res

    @api.model
    def get_default_values(self, fields):
        conf = self.env['ir.config_parameter']
        return {
            'api_key': conf.get_param('api_key'),
            'api_server_message': conf.get_param('api_server_message'),
            'timeout': int(conf.get_param('timeout')),
            'archive_timeout': int(conf.get_param('archive_timeout')),
            'api_balance': float(conf.get_param('api_balance')),
            'api_username': conf.get_param('api_username'),
            'api_login': conf.get_param('api_login'),
            'api_phone': conf.get_param('api_phone'),
            'api_registered_partner_ids': json.loads(
                conf.get_param('api_registered_partner_ids') or '[]')
        }

    @api.one
    def set_values(self):
        conf = self.env['ir.config_parameter']
        conf.set_param('api_key', str(self.api_key))
        conf.set_param('api_server_message',
                       (normalize('NFKD',
                                  unicode(self.api_server_message or '')).
                        encode('ASCII', 'ignore')))
        conf.set_param('api_balance', str(self.api_balance))
        conf.set_param('timeout', str(self.timeout))
        conf.set_param('archive_timeout', str(self.archive_timeout))
        conf.set_param('api_username',
                       (normalize('NFKD', unicode(self.api_username or '')).
                        encode('ASCII', 'ignore')))
        conf.set_param('api_login', str(self.api_login))
        conf.set_param('api_phone', str(self.api_phone))
        conf.set_param('api_registered_partner_ids',
                       str(self.api_registered_partner_ids.ids))

    def get_timeout(self):
        """
        Get the timeout config field
        :return: the int timeout
        """

        time_out = self.env['ir.config_parameter'].get_param('timeout')
        return int(time_out)

    def get_archive_timeout(self):
        """
        Get the archive_timeout config field
        :return: the int archive_timeout
        """

        archive_time_out = self.env['ir.config_parameter'].get_param('archive_timeout')
        return int(archive_time_out)

    def get_client(self, _raise=True):
        """
        :return: The Totalvoice Client Object
        """
        try:
            api_key = self.env['ir.config_parameter'].get_param('api_key')

            if not api_key:
                raise UserError(_('API-KEY not configured. Check the '
                                  'Totalvoice Configuration section'))

            client = Cliente(api_key, api_url,)

        except Exception:
            if _raise:
                raise UserError(_('API-KEY and API-URL not configured. Check '
                                  'the Totalvoice Configuration section'))

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

    def action_update_registered_partner_numbers(self):
        """
        This method updates the registered_partner_numbers
        """

        updated_res_partner_ids = self.update_registered_partner_numbers()

        if updated_res_partner_ids:
            updated_res_partner_ids = updated_res_partner_ids.ids

            self.env['ir.config_parameter'].set_param(
                'api_registered_partner_ids',
                str(updated_res_partner_ids))

        return True

    def update_registered_partner_numbers(self):
        """
        This method returns an updated registered partner numbers o2m field,
        including the new numbers that have been added to the TotalVoice
        Account since the last sync and excluding the old numbers not
        registered anymore.
        Note: If an number is registered but there isn't any partner carrying
        it, a new partner won't be created with this number.

        :return: an updated registered partner numbers o2m field
        """

        # If the user updated the API-KEY
        if self.api_key:
            self.env['ir.config_parameter'].set_param('api_key', self.api_key)

        bina_report = {}

        try:
            bina_report = json.loads(self.get_client().bina.get_relatorio())
        except Exception:
            bina_report['mensagem'] = _('Problem when connecting to the '
                                        'TotalVoice Server')

        message = bina_report.get('mensagem')

        if self:
            self.api_server_message = message

        self.env['ir.config_parameter'].set_param(
            'api_server_message', message)

        # api_balance
        api_balance = 0
        try:
            api_balance = json.loads(
                self.get_client().minha_conta.get_saldo()) \
                .get('dados').get('saldo')
        except Exception:
            api_balance = 0

        if self:
            self.api_balance = api_balance

        self.env['ir.config_parameter']. \
            set_param('api_balance', str(api_balance))

        if not bina_report.get('dados'):
            return

        registered_partner_ids = self.env['res.partner'].browse(
            json.loads(self.env['ir.config_parameter'].
                       get_param('api_registered_partner_ids') or '[]')
        )

        new_registered_partner_ids = self.env['res.partner']

        # For every number registered in the Totalvoice's system
        for bina in bina_report.get('dados').get('relatorio'):
            phone_number = bina.get('numero_telefone')

            # Looking for partners containing the phone_number
            partners = self.env['res.partner'].search(['|',
                                                       ('phone', '!=', False),
                                                       ('mobile', '!=', False),
                                                       ]).filtered(
                lambda r: phone_number in [
                    self.number_to_raw(r.phone),
                    self.number_to_raw(r.mobile),
                ]
            )

            new_registered_partner_ids += partners

            for partner in partners:
                self.register_partner(partner, phone_number)

        # Remove the old registered_partners
        for partner in (registered_partner_ids - new_registered_partner_ids):
            self.remove_partner(partner)

        return new_registered_partner_ids

    def verify_registered_number(self, number):
        """
        Verifies if the specified number is already registered in
        TotalVoice for the configured account
        :param number: number to be verified
        :return: True if the number is already registered. Else if it's not
        """

        try:
            bina_report = json.loads(self.get_client().bina.get_relatorio())

            already_registered = \
                any(number == bina.get('numero_telefone')
                    for bina in bina_report.get('dados').get('relatorio'))

            return True if already_registered else False

        except:
            return True

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

            registered_partners += partner
            if partner not in registered_partners:
                self.env['ir.config_parameter'].set_param(
                    'api_registered_partner_ids', str(registered_partners.ids))
            if self:
                self.api_registered_partner_ids = registered_partners


    def remove_partner(self, partner):
        """
        Remove res_partner from the api_registered_partner_ids list
        """
        partner.totalvoice_number = False

        registered_partners = self.env['res.partner']. \
            browse(self.get_default_values(None).
                   get('api_registered_partner_ids'))
        registered_partners -= partner
        if self:
            self.api_registered_partner_ids = registered_partners
        self.env['ir.config_parameter'].set_param(
            'api_registered_partner_ids', str(registered_partners.ids))

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

    def action_test_webhook_message(self):
        totalvoice_webhook = \
            self.env['webhook'].search([('name', '=', 'totalvoice')], limit=1)

        json = {
            "id": self.api_test_webhook_id,
            "sms_id": self.api_test_webhook_sms_id,
            "resposta": self.api_test_webhook_message,
            "data_resposta": fields.Datetime.now(),
        }

        totalvoice_webhook.run_totalvoice_totalvoice(json=json,
                                                     partner=self.partner_id)
