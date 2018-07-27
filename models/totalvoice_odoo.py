# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

from totalvoice.cliente import Cliente
import json
import re

client = Cliente("49c31c417f21915f1ced29182c5dea56", 'api.totalvoice.com.br')
date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
date_format_webhook = '%Y-%m-%dT%H:%M:%S-%f:00'

class WebHook(models.Model):
    _inherit = 'webhook'

    totalvoice_id = fields.Many2one(
        comodel_name='totalvoice.base',
    )

    @api.one
    def run_totalvoice_https(self):
        # You will have all request data in
        # variable: self.env.request
        return self.totalvoice_id.get_sms_status(
            received_message=[self.env.request.jsonrequest])



class TotalVoiceMessage(models.Model):
    _name = 'totalvoice.message'

    sms_id = fields.Integer(
        string='SMS ID',
        readonly=True,
        help="SMS ID provided by Total Voice's server"
    )

    active_sms_id = fields.Integer(
        string='SMS ID',
        readonly=True,
        invisible=True,
        help="Active SMS ID waiting for answers"
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
                   ('received', 'Received')],
        default='received',
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

    answer_ids = fields.One2many(
        comodel_name='totalvoice.message',
        inverse_name='coversation_id',
        string='Contact Answers',
        readonly=True,
        invisible=True,
    )

    webhook_id = fields.One2many(
        comodel_name='webhook',
        inverse_name='totalvoice_id',
        string='Webhook',
        readonly=True,
        invisible=True,
        default=lambda self: self.env.ref(
            'totalvoice_odoo.webhook_totalvoice'),
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
        selection=[('assign_task', 'Assign a Task')],
        default='assign_task',
    )

    number_to = fields.Char(
        string='Phone',
        related='partner_id.mobile',
        readonly=True,
        help="Contact's number",
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

    server_message = fields.Char(
        string='Server Message',
        readonly=True,
        size=160,
    )

    @api.depends('number_to')
    def _number_to_raw(self):
        self.number_to_raw = re.sub('\D', '', self.number_to)

    @api.multi
    def send_sms(self, env=False, message=False, wait=True):
        """
        Send an SMS to the selected res_partner
        :param message: If this isn't None, then the SMS sent will be added
        in the conversation as a reply to the user's last answer
        :param wait: Should this message wait for new answers?
        """
        for record in self:

            send_message = message or record.message
            wait_for_answer = wait and record.wait_for_answer
            response = client.sms.enviar(
                record.number_to_raw, send_message,
                resposta_usuario=wait_for_answer
            )

            response = json.loads(response)
            data = response.get('dados')

            if not wait_for_answer:
                record.state = 'done'
            else:
                record.state = 'waiting'

            # if this function is being called for the first time in this
            # conversation
            if not message:

                record.server_message = 'Motivo: ' + \
                                        str(response.get('motivo')) + ' - ' + \
                                        response.get('mensagem')

                if not response.get('sucesso'):
                    record.state = 'failed'
                    return

                record.sms_id = record.active_sms_id = data.get('id')

                record.message_date = fields.Datetime.now()

            # Else means that the system is replying the user with a new SMS
            else:
                record.active_sms_id = data.get('id')

                new_message = {
                    'message_date': fields.Datetime.now(),
                    'sms_id': data.get('id'),
                    'message': send_message,
                    'coversation_id': record.id,
                    'message_origin': 'sent',
                }

                self.env['totalvoice.message'].create(new_message)

    @api.multi
    def get_sms_status(self, env=False, received_message=False):
        for record in self:

            answers = received_message or \
                      json.loads(
                          client.sms.get_by_id(str(record.active_sms_id))).\
                          get('dados').get('respostas')

            if answers:
                for answer in answers:
                    if answer['id'] in record.answer_ids.mapped('sms_id'):
                        continue
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
                    self.review_sms_answer(answer_id)

    def review_sms_answer(self, answer):
        if not answer.message:
            return
        func = str(self.subject) + '_' + str(answer.message)
        try:
            eval('self.%s()' % func)
        except Exception:
            new_message = 'Opcao selecionada invalida. Tente novamente. ' + \
                          self.message
            if self.auto_resend:
                self.send_sms(message=new_message, wait=True)

        finally:
            return

    def assign_task_0(self):
        if not self.auto_resend:
            return
        new_message = "Opcao Selecionada: 0. Voce NAO foi designado a tarefa."
        return self.send_sms(message=new_message, wait=False)

    def assign_task_1(self):
        if not self.auto_resend:
            return
        new_message = "Opcao Selecionada: 1. Voce foi designado a tarefa."
        return self.send_sms(message=new_message, wait=False)
