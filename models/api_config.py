# -*- coding: utf-8 -*-

from odoo import api, fields, models
from totalvoice.cliente import Cliente

class ApiConfig(models.TransientModel):
    _name = 'totalvoice.api.config'
    _inherit = 'res.config.settings'

    api_key = fields.Char(
        string='API-KEY',
    )
    api_url = fields.Char(
        string='API-URL',
    )

    @api.model
    def get_default_values(self, fields):
        conf = self.env['ir.config_parameter']
        return {
            'api_key': conf.get_param('api_key'),
            'api_url': conf.get_param('api_url'),
        }

    @api.one
    def set_values(self):
        conf = self.env['ir.config_parameter']
        conf.set_param('api_key', str(self.api_key))
        conf.set_param('api_url', str(self.api_url))

    def get_client(self):
        """
        :return: The Totalvoice Client Object
        """
        return Cliente(self.env['ir.config_parameter'].get_param('api_key'),
                       self.env['ir.config_parameter'].get_param('api_url'))
