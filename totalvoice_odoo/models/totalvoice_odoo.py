# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

import logging
import random
import json
import re

date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
date_format_webhook = '%Y-%m-%dT%H:%M:%S-%f:00'

MAXIMUM_CONVERSATION_CODES = 1000
log = logging.getLogger(__name__)

PHONE_SELECTION = [
    ('phone', _('Phone')),
    ('mobile', _('Mobile')),
]


class WebHook(models.Model):
    _inherit = 'webhook'

    @api.one
    def run_totalvoice_totalvoice(self, json=False):
        # You will have all request data in
        # variable: self.env.request

        received_message = json or self.env.request.jsonrequest
        message = received_message.get('resposta')

        conversation_code = re.split(r'[^a-zA-Z\d:]', message)[0]

        conversation_id = self.env['totalvoice.base'].search(
            [('conversation_code', '=',
              ''.join('%03d' % int(conversation_code))),
             ('state', 'in', ['waiting'])], limit=1
        )

        if conversation_id:
            return conversation_id.get_sms_status(
                received_message=received_message)

        self.send_message_wrong_code(conversation_code, received_message)

    def send_message_wrong_code(self, conversation_code, json):
        """
        This method is called if there isn't any active conversation using the
        code specified in the SMS answer.
        """

        # First we'll find the conversation the user tried to answer
        received_message = json

        sms_id = received_message.get('sms_id')

        conversation_id = self.env['totalvoice.base'].search(
            [('sms_id', '=', sms_id)]
        )

        # There isn't a conversation_id for this user
        if not conversation_id:
            return

        # Getting the res_partner
        res_partner = conversation_id.partner_id

        # Searching the available conversation_codes for this specific
        # res_partner

        available_conversation_codes = conversation_id.search(
            [('partner_id', '=', res_partner.id),
             ('state', 'in', ['waiting'])]
        ).mapped('conversation_code')

        message = _('Unavailable code received: ') + conversation_code + '. '
        if len(available_conversation_codes):
            message += _('Available codes are: ') + \
                       ''.join('%03d' % int(code) + ", "
                               for code in available_conversation_codes)
        else:
            message += "There isn't any code availables for you to answer to."

        # Create a new conversation for sending an Code Error message
        conversation_id = self.env['totalvoice.base'].create({
            'partner_id': res_partner.id,
        })

        conversation_id.send_sms(custom_message=message, wait=False)


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

    STATES = [('draft', 'Draft'),
              ('waiting', 'Waiting Answer'),
              ('timeout', 'Answer Time Out'),
              ('done', 'Done'),
              ('failed', 'Failed')]

    FOLDED_STATES = [
        'draft',
    ]

    conversation_code = fields.Char(
        string=_("Conversation Code"),
        help=_("This code will be used as an ID for identifying answers."),
        readonly=True,
        size=3,
    )

    active = fields.Boolean(
        string=_('Active'),
        default=True,
    )

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
        selection=STATES,
        default='draft',
        readonly=True,
    )

    subject = fields.Selection(
        string='Subject',
        selection=[],
    )

    number_to = fields.Selection(
        selection=PHONE_SELECTION,
        string='Phone Selected',
        required=True,
        default='mobile'
    )

    number_to_phone = fields.Char(
        string="Phone",
        related='partner_id.phone',
    )

    number_to_mobile = fields.Char(
        string="Mobile",
        related='partner_id.mobile',
    )

    number_to_raw = fields.Char(
        compute='_number_to_raw',
        store=True,
    )

    wait_for_answer = fields.Boolean(
        default=True,
    )

    conversation_done_date = fields.Datetime(
        readonly=True,
    )

    @api.model
    def state_groups(self, present_id, domain, **kwargs):
        folded = {key: (key in self.FOLDED_STATES) for key, _ in self.STATES}
        return self.STATES[:], folded

    _group_by_full = {
        'state': state_groups,
    }

    @api.model
    def create(self, values):
        if not values.get('conversation_code'):
            values['conversation_code'] = self.get_conversation_code()
        res = super(TotalVoiceBase, self).create(values)
        self._cr.commit()
        return res

    @api.multi
    def write(self, vals):
        # params = self.env.args[2].get('params')
        # if params and params.get('view_type') == 'kanban' and \
        #         'state' in vals:
        #     raise UserError(_("You can't move this card"))

        return super(TotalVoiceBase, self).write(vals)

    @api.one
    @api.depends('state')
    def _set_state_date(self):
        """
        If the conversation state is set to 'done', a timer will be set to
        fields.Datetime.now()
        """

        if self.state == 'done':
            self.conversation_done_date = fields.Datetime.now()

    @api.onchange('partner_id')
    def onchange_update_default_number_to(self):
        """
        Updates the default number_to value each time the partner_id changes.
        Set the number_to selection value, evaluating which one of the
        mobile\phone field is available
        """
        if self.number_to_phone and not self.number_to_mobile:
            self.number_to = 'phone'
        else:
            self.number_to = 'mobile'

    @api.depends('number_to')
    def _number_to_raw(self):
        """
        Remove any characters other then numbers from partner's phone number
        """
        for record in self:
            number = ''

            if record.number_to == 'phone':
                number = record.number_to_phone
            elif record.number_to == 'mobile':
                number = record.number_to_mobile

            record.number_to_raw = re.sub('\D', '', number or '').lstrip('0')

    @api.model
    def cron_check_message_timeout(self):
        """
        Iterates over all the "Waiting for Answer" messages, updating their
        states to "Time Out" if necessary
        """
        conversations = self.search([('state', 'in', ['waiting', 'done'])])

        for conversation in conversations:
            conversation.update_conversation_state()

    def update_conversation_state(self):
        """
        This method updates the conversation state based on the time spent from
        the message sent to the method call.
        If this time is greater or equal "MESSAGE_TIMEOUT_HOURS", the new state
        will be 'waiting'.
        If the conversation has no active_message, the state will be 'done'

        This method also archives the conversation if it's older than
        'archive_conversation_date', on the API Config
        :return: Nothing if the conversation has no active_message
        """

        active_message = self.active_sms_id

        if not active_message:
            self.state = 'done'
            return

        now_date = datetime.now()
        
        if self.state == 'waiting':
            active_message_id = self.message_ids.filtered(
                lambda m: m.sms_id == active_message
            )
            message_date = fields.Datetime.from_string(
                active_message_id.message_date)
    
            delta = (now_date - message_date)
            hours_passed = delta.total_seconds() // 3600
    
            # if the message is older than MESSAGE_TIMEOUT_HOURS
            if hours_passed >= self.env['totalvoice.api.config'].get_timeout():
                self.state = 'timeout'

        elif self.state == 'done':
            conversation_done_date = fields.Datetime.from_string(
                self.conversation_done_date
            )
    
            if conversation_done_date:
                delta = now_date - conversation_done_date
                hours_passed = delta.total_seconds() // 3600
    
                if hours_passed >= self.env['totalvoice.api.config'].\
                        get_archive_timeout():
                    self.active = False
            else:
                self.conversation_done_date = fields.Datetime.now()

    def get_conversation_code(self):
        """
        Get a random conversation code available based on the existing
        active conversations.
        This method also sets the self.conversation_code to the code found
        :return: the smallest available conversation code
        """

        random_code = False

        active_codes = self.search([('state', 'in', ['draft', 'waiting'])]
                                   ).mapped('conversation_code')

        available_codes = list(set(range(1, MAXIMUM_CONVERSATION_CODES)) -
                               set(map(int, active_codes)))

        if len(available_codes) > 0:
            random_code = self.conversation_code \
                if self.conversation_code in available_codes \
                else ''.join('%03d' % random.choice(available_codes))

            if self.id:
                self.conversation_code = random_code

        return random_code

    @api.multi
    def send_sms(self, env=False, custom_message=False, wait=None, multi_sms=True):
        """
        Send an SMS to the selected res_partner
        :param message: If this isn't None, then the SMS sent will be added
        in the conversation as a reply to the user's last answer
        :param wait: Should this message wait for new answers?
        :return: True if send is OK, False if it's not OK
        """
        for record in self:
            if (record.number_to == 'phone' and not record.number_to_phone) or\
                    (record.number_to == 'mobile' and
                     not record.number_to_mobile):
                raise ValidationError(_("The contact you want to send a "
                                        "message to needs to have a "
                                        "valid selected number"))

            send_message = custom_message or record.message

            if not send_message:
                raise ValidationError(_("The SMS needs to have a message."))

            record.message = send_message
            wait_for_answer = record.wait_for_answer if wait is None else wait
            record.wait_for_answer = wait_for_answer

            if(record.state not in ['draft', 'waiting']):
                # Get a new conversation code to this conversation
                if not self.get_conversation_code():
                    record.state = 'failed'

                    new_message = {
                        'message_date': fields.Datetime.now(),
                        'message': send_message,
                        'coversation_id': record.id,
                        'message_origin': 'error',
                    }

                    new_message['server_message'] = \
                        _("There's not free conversation_code left for "
                          "sending this message")

                    self.env['totalvoice.message'].create(new_message)

                    self.cr.commit()

                    raise StandardError(_("There's not free conversation_code "
                                          "left for sending this message"))

            # Sends the SMS
            response = \
                self.env['totalvoice.api.config'].get_client().sms.enviar(
                    record.number_to_raw, send_message,
                    resposta_usuario=True,
                    multi_sms=multi_sms
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

                # 'Motivo=8' means the number isn't registered at
                # Totalvoice Configuration. So we need to remove the
                # partner from the api_registered_partner_ids
                if response.get('motivo') == 8:
                    self.env['totalvoice.api.config'].\
                        remove_partner(self.partner_id)
                    new_message['server_message'] = \
                        _('Number not registered on TotalVoice')

                self.env['totalvoice.message'].create(new_message)

                return False

            # If this conversation isn't waiting for an answer
            if not wait_for_answer:
                record.state = 'done'
            else:
                record.state = 'waiting'

            data = response.get('dados')

            sms_ids = data.get('id')
            record.active_sms_id = sms_ids \
                if type(sms_ids) is int \
                else sms_ids[-1]

            record.sms_id = record.sms_id \
                if record.sms_id \
                else record.active_sms_id

            new_message = {
                'message_date': fields.Datetime.now(),
                'sms_id': record.active_sms_id,
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

                new_answers = [a for a in answers if a['id']
                               not in record.message_ids.mapped('sms_id')]

                # Set the state to DONE:
                if new_answers:
                    record.state = 'done'

                for answer in new_answers:

                    try:
                        message_date = datetime.strptime(
                            answer['data_resposta'], date_format_webhook)
                    except:
                        try:
                            message_date = datetime.strptime(
                                answer['data_resposta'], date_format)
                        except:
                            message_date = answer['data_resposta']

                    new_answer = {
                        'message_date': message_date,
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
        """

        return self.send_sms(custom_message=message, wait=wait)

    def review_sms_answer(self, answer):
        """
        Handles the received message.
        :param answer: Received message
        """
        if not answer.message:
            return

        # Building the function that will be called to handle this message
        func_name = re.split(r'[^a-zA-Z\d:]', answer.message)[0]
        # func = self.subject + '_' + func_name
        parameters = answer.message.replace(func_name, '').strip()

        # If there isn't an subject, the message won't be reviewed
        func = self.subject
        if not func:
            return

        try:
            eval("self.%s(%s)" %
                 (func, "'" + parameters + "'" if parameters else ''))
        except Exception:
            log_message = _("An error was triggered processing the message. "
                            "Please try again. ") + self.message
            log.debug(log_message)

        finally:
            return

    def action_register_number(self):
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
