# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError

import json
import re

date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
date_format_webhook = '%Y-%m-%dT%H:%M:%S-%f:00'

class WebHook(models.Model):
    _inherit = 'webhook'

    @api.one
    def run_totalvoice_https(self):
        # You will have all request data in
        # variable: self.env.request
        sms_id = self.env.request.jsonrequest.get('sms_id')
        conversation_id = \
            self.env['totalvoice.base'].search([('sms_id', '=', sms_id)])

        return conversation_id.get_sms_status(
            received_message=self.env.request.jsonrequest)



class TotalVoiceMessage(models.Model):
    _name = 'totalvoice.message'

    sms_id = fields.Integer(
        string='SMS ID',
        readonly=True,
        help=_("SMS ID provided by Total Voice's server"),
    )

    active_sms_id = fields.Integer(
        string='SMS ID',
        readonly=True,
        invisible=True,
        help=_("Active SMS ID waiting for answers"),
    )

    coversation_id = fields.Many2one(
        comodel_name='totalvoice.base',
        string='TotalVoice Conversation',
    )

    message = fields.Text(
        string='Message',
        size=160,
    )

    message_date = fields.Datetime(
        string='Message Date',
        readonly=True,
    )

    message_origin = fields.Selection(
        selection=[('sent', 'Sent'),
                   ('received', 'Received'),
                   ('error', 'Error')],
        default='received',
    )

    server_message = fields.Char(
        string='Server Message',
        readonly=True,
        size=160,
    )


class TotalVoiceBase(models.Model):
    _name = 'totalvoice.base'
    _inherits = {'totalvoice.message': 'message_id'}
    _rec_name = 'partner_id'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact',
        required=True,
        domain="[('mobile', '!=', False)]",
    )

    image = fields.Binary(
        string='Contact Avatar',
        related='partner_id.image',
        readonly=True,
    )

    image_medium = fields.Binary(
        related='partner_id.image_medium',
    )

    image_small = fields.Binary(
        related='partner_id.image_small',
    )

    message_id = fields.Many2one(
        comodel_name='totalvoice.message',
        string='message_id',
        readonly=True,
        invisible=True,
        required=True,
        ondelete='cascade',
    )

    message_ids = fields.One2many(
        comodel_name='totalvoice.message',
        inverse_name='coversation_id',
        string='Conversation Messages',
        readonly=True,
        invisible=True,
    )

    state = fields.Selection(
        selection=[('draft', 'Draft'),
                   ('waiting', 'Waiting Answer'),
                   ('done', 'Done'),
                   ('failed', 'Failed')],
        default='draft',
        readonly=True,
    )

    subject = fields.Selection(
        string='Subject',
        selection=[],
    )

    number_to = fields.Char(
        string='Phone',
        related='partner_id.mobile',
        readonly=True,
        help=_("Contact's number"),
    )

    number_to_raw = fields.Char(
        compute='_number_to_raw',
        store=True,
    )

    wait_for_answer = fields.Boolean(
        default=False,
    )

    auto_resend = fields.Boolean(
        string='Auto-Resend',
        default=True,
    )

    @api.multi
    def write(self, vals):
        if self.env.args[2].get('params').get('view_type') == 'kanban' and \
                'state' in vals:
            raise UserError(_("You can't move this card"))

        return super(TotalVoiceBase, self).write(vals)

    @api.depends('number_to')
    def _number_to_raw(self):
        """
        Remove any characters other then numbers from partner's phone number
        """
        self.number_to_raw = re.sub('\D', '', self.number_to or '')

    @api.multi
    def send_sms(self, env=False, custom_message=False, wait=None):
        """
        Send an SMS to the selected res_partner
        :param message: If this isn't None, then the SMS sent will be added
        in the conversation as a reply to the user's last answer
        :param wait: Should this message wait for new answers?
        :return: True if send is OK, False if it's not OK
        """
        for record in self:

            send_message = custom_message or record.message
            record.message = send_message
            wait_for_answer = record.wait_for_answer if wait is None else wait
            record.wait_for_answer = wait_for_answer

            # Sends the SMS
            response = \
                self.env['totalvoice.api.config'].get_client().sms.enviar(
                    record.number_to_raw, send_message,
                    resposta_usuario=wait_for_answer
            )

            response = json.loads(response)

            server_message = 'Motivo: ' + str(response.get('motivo')) \
                             + ' - ' + response.get('mensagem')

            record.message_date = fields.Datetime.now()

            # If the message couldn't be sent
            if not response.get('sucesso'):
                record.state = 'failed'

                new_message = {
                    'message_date': fields.Datetime.now(),
                    'message': send_message,
                    'coversation_id': record.id,
                    'message_origin': 'error',
                    'server_message': server_message
                }

                self.env['totalvoice.message'].create(new_message)

                return False

            # If this conversation isn't waiting for an answer
            if not wait_for_answer:
                record.state = 'done'
            else:
                record.state = 'waiting'

            data = response.get('dados')

            record.active_sms_id = data.get('id')

            record.sms_id = record.sms_id \
                if record.sms_id \
                else record.active_sms_id

            new_message = {
                'message_date': fields.Datetime.now(),
                'sms_id': data.get('id'),
                'message': send_message,
                'coversation_id': record.id,
                'message_origin': 'sent',
                'server_message': server_message
            }

            self.env['totalvoice.message'].create(new_message)
            return True

    @api.multi
    def get_sms_status(self, env=False, received_message=False):
        """
        :param received_message: Message received by the Webhook
        """
        for record in self:

            answers = (received_message and [received_message]) or \
                      json.loads(self.env['totalvoice.api.config'].
                                 get_client().
                                 sms.get_by_id(str(record.active_sms_id))).\
                          get('dados').get('respostas')

            if answers:
                for answer in \
                        [a for a in answers
                         if a['id']
                            not in record.message_ids.mapped('sms_id')]:
                    new_answer = {
                        'message_date': datetime.strptime(
                            answer['data_resposta'],
                            ((received_message and date_format_webhook)
                             or date_format)),
                        'sms_id': answer['id'],
                        'message': answer['resposta'],
                        'coversation_id': record.id,
                    }
                    answer_id = \
                        self.env['totalvoice.message'].create(new_answer)
                    record.review_sms_answer(answer_id)

    def resend_message(self, message=False, wait=False):
        """
        Sends an automatic response depending on the user's previous response
        :param message: Message to be sent
        :param wait: Should the conversation wait for new answers?
        :return: True if send is OK, False if it's not OK
        """
        # It only sends the response if the variable 'auto_resend' is true
        if self.auto_resend:
            return self.send_sms(custom_message=message, wait=wait)
        return False

    def review_sms_answer(self, answer):
        """
        Handles the received message.
        :param answer: Received message
        """
        if not answer.message:
            return
        func_name = re.split(r'[^a-zA-Z\d:]', answer.message)[0]
        func = self.subject + '_' + func_name
        parameters = answer.message.replace(func_name, '').strip()
        try:
            eval("self.%s(%s)" %
                 (func, "'" + parameters + "'" if parameters else ''))
        except Exception:
            new_message = 'Opcao selecionada invalida. Tente novamente. ' + \
                          self.message

            self.resend_message(message=new_message, wait=True)

        finally:
            return
