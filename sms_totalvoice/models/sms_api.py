# Copyright 2019 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

DEFAULT_ENDPOINT = 'api.totalvoice.com.br'

from odoo import api, fields, models, _

from totalvoice.cliente import Cliente


class SmsApi(models.AbstractModel):

    _inherit = 'sms.api'

    @api.model
    def _send_sms(self, numbers, message):
        """ Send sms
        """
        account = self.env['iap.account'].get('sms')
        for number in numbers:
            cliente = Cliente(account.account_token, DEFAULT_ENDPOINT)
            r = cliente.sms.enviar(number, message)
        return True