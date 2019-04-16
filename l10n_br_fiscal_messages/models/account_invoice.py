# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2016 Kmee - www.kmee.com.br
#   @author Luiz Felipe do Divino
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import os
import logging
import datetime

from openerp.tools.translate import _
from openerp import models, fields, api
from openerp.exceptions import RedirectWarning

from openerp.addons.nfe.sped.nfe.nfe_factory import NfeFactory
from openerp.addons.nfe.sped.nfe.validator.xml import XMLValidator
from openerp.addons.nfe.sped.nfe.processing.xml import send, cancel
from openerp.addons.nfe.sped.nfe.processing.xml import monta_caminho_nfe
from openerp.addons.nfe.sped.nfe.processing.xml import check_key_nfe
from openerp.addons.nfe.sped.nfe.validator.config_check import \
    validate_nfe_configuration, validate_invoice_cancel

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    """account_invoice overwritten methods"""
    _inherit = 'account.invoice'

    @api.multi
    def nfe_export(self):

        for inv in self:

            validate_nfe_configuration(inv.company_id)

            nfe_obj = self._get_nfe_factory(inv.nfe_version)

            messages_invoice = []

            messages_invoice.append(
                inv.company_id.invoice_message.message_invoice
            )

            for invoice_line in inv.invoice_line:
                for fiscal_position in invoice_line.fiscal_position:
                    if fiscal_position.message_id:
                        messages_invoice.append(
                            fiscal_position.message_id.message_invoice
                        )
                for fiscal_category_id in invoice_line.fiscal_category_id:
                    if fiscal_category_id.message_id:
                        messages_invoice.append(
                            inv.fiscal_category_id.message_id.message_invoice
                        )

            if messages_invoice:
                messages_list = []

                for message in messages_invoice:
                    if message not in messages_list:
                        messages_list.append(message)

                if inv.comment:
                    inv.comment += ' - ' + ' - '.join(messages_list)
                else:
                    inv.comment = ' - '.join(messages_list)

            # nfe_obj = NFe310()
            nfes = nfe_obj.get_xml(self.env.cr, self.env.uid, self.ids,
                                   int(inv.company_id.nfe_environment),
                                   self.env.context)

            for nfe in nfes:
                # erro = nfe_obj.validation(nfe['nfe'])
                erro = XMLValidator.validation(nfe['nfe'], nfe_obj)
                nfe_key = nfe['key'][3:]
                if erro:
                    raise RedirectWarning(
                        erro, _(u'Erro na validaço da NFe!'))

                inv.write({'nfe_access_key': nfe_key})
                save_dir = os.path.join(
                    monta_caminho_nfe(
                        inv.company_id,
                        chave_nfe=nfe_key) +
                    'tmp/')
                nfe_file = nfe['nfe'].encode('utf8')

                file_path = save_dir + nfe_key + '-nfe.xml'
                try:
                    if not os.path.exists(save_dir):
                        os.makedirs(save_dir)
                    f = open(file_path, 'w')
                except IOError:
                    raise RedirectWarning(
                        _(u'Erro!'), _(u"""Não foi possível salvar o arquivo
                            em disco, verifique as permissões de escrita
                            e o caminho da pasta"""))
                else:
                    f.write(nfe_file)
                    f.close()

                    event_obj = self.env['l10n_br_account.document_event']
                    event_obj.create({
                        'type': '0',
                        'company_id': inv.company_id.id,
                        'origin': '[NF-E]' + inv.internal_number,
                        'file_sent': file_path,
                        'create_date': datetime.datetime.now(),
                        'state': 'draft',
                        'document_event_ids': inv.id
                    })
                    inv.write({'state': 'sefaz_export'})
