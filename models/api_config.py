# -*- coding: utf-8 -*-

from odoo import api, fields, models
from totalvoice.cliente import Cliente

import json

class ApiConfig(models.TransientModel):
    _name = 'totalvoice.api.config'
    _inherit = 'res.config.settings'

    api_key = fields.Char(
        string='API-KEY',
    )
    api_url = fields.Char(
        string='API-URL',
    )

    api_balance = fields.Float(
        string='Balance',
        readonly=True,
    )

    @api.model
    def default_get(self, fields):
        res = super(ApiConfig, self).default_get(fields)

        # api_balance
        res['api_balance'] = json.loads(self.get_client().minha_conta.
                                        get_saldo()).get('dados').get('saldo')
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
        }

    @api.one
    def set_values(self):
        conf = self.env['ir.config_parameter']
        conf.set_param('api_key', str(self.api_key))
        conf.set_param('api_url', str(self.api_url))
        conf.set_param('api_balance', str(self.api_balance))

    def get_client(self):
        """
        :return: The Totalvoice Client Object
        """
        return Cliente(self.env['ir.config_parameter'].get_param('api_key'),
                       self.env['ir.config_parameter'].get_param('api_url'))
