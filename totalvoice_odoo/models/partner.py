# -*- coding: utf-8 -*-

import urlparse

from odoo import api, fields, models, tools, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    notify_sms = fields.Selection([
        ('none', 'Never'),
        ('always', 'All Messages')],
        'SMS Messages and Notifications',
        required=True,
        default='none',
        help="Policy to receive sms for new messages pushed to your personal Inbox:\n"
             "- Never: no sms are sent\n"
             "- All Messages: for every notification you receive in your Inbox"
    )
    totalvoice_number = fields.Char(
        string="TotalVoice Number",
        store=True,
    )

    def _notify(self, message, force_send=False, send_after_commit=True, user_signature=True):
        """
        :param message:
        :param force_send:
        :param send_after_commit:
        :param user_signature:
        :return:
        """
        result = super(ResPartner, self)._notify(
            message=message,
            force_send=force_send,
            send_after_commit=send_after_commit,
            user_signature=user_signature,
        )
        message_sudo = message.sudo()

        ### TODO: Verificar se este filtro é mesmo necessário
        email_channels = message.channel_ids.filtered(lambda channel: channel.email_send)
        ####

        self.sudo().search([
            '|',
            ('id', 'in', self.ids),
            ('channel_ids', 'in', email_channels.ids),
            ('email', '!=', message_sudo.author_id and message_sudo.author_id.email or message.email_from),
            ('notify_sms', '!=', 'none')
        ])._notify_by_sms(
            message,
            force_send=force_send,
            send_after_commit=send_after_commit,
            user_signature=user_signature
        )
        return result

    @api.multi
    def _notify_by_sms(self, message, force_send=False, send_after_commit=True, user_signature=True):
        """
        Quando uma mensagem é enviada o atributo message.message_id representa um identificador único
        da mensagem por exemplo:

        message_id = u'<1547167155.792278051376343.731946976816807-openerp-31-product.template@mileo-xps>'

        Quando o email de resposta é enviado para o email de catchall (apenas um email de entrada que
        recebe todos os emails de resposta o sistema identifica este id e link a resposta a tread relacionada.

        Ainda existe um método message_new que processa o conteudo do email de resposta para executar
        ações no documento como por exemplo: parts.server.addons.hr_expense.models.hr_expense.HrExpense#message_new


        # TODO: Enviar mensagem sms para os seguidores
        # TODO: Enviar sms com link para os seguidores
        # TODO: Processasr sms de resposta e colocar a resposta nas respostas da tread,
            se for o caso processar algo (exemplo: avançar um workflow, modificar algum registro e etc);
        """
        thread_id = self.env['mail.thread']

        # classify recipients: actions / no action
        if message.model and message.res_id and hasattr(self.env[message.model], '_message_notification_recipients'):
            thread_id = self.env[message.model].browse(message.res_id)

        if thread_id and self._context.get('auto_delete', False):
            access_link = thread_id._notification_link_helper('view')
        else:
            access_link = thread_id._notification_link_helper('view', message_id=message.id)

        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        complete_link = urlparse.urljoin(base_url, access_link)

        link = self.env['link.tracker'].create({
            'url': complete_link,
        })

        for partner in self:

            # TODO: Enviar um sms para multiplos números???

            totalvoice_base_obj = self.env['totalvoice.base']
            totalvoice_base = totalvoice_base_obj.create({
                'partner_id': partner.id,
            })

            sms_text = tools.html2text(message.body)
            message = sms_text[:130] + '...\n' + link.short_url
            totalvoice_base.send_sms(custom_message=message)
