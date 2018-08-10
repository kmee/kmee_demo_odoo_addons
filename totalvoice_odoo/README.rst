===============
TotalVoice Odoo
===============

Module created to integrate the TotalVoice API with Odoo.

This module manage to send and receive SMS messages, invoking
methods to process the webhook events.

Configuration
=============

First, you will need to `create a TotalVoice Account <https://www.totalvoice.com.br/signup.php>`_

After creating you account, the next step is to configure your 'Webhook de
Resposta de SMS' in the 'Minha Conta / Configurações da API' menu.

In this page, you should set the 'Webhook de Resposta de SMS' field with
your **webhook url**. For example:

.. code-block:: xml

    http://prod.yourcompany.odoo.com.br/webhook/totalvoice

Notice the **webhook/totalvoice** after your Odoo URL. That is important.

The next step is to retrieve your **Access-Token**. It can be found in the
`website main panel <https://api.totalvoice.com.br/painel> _`

Now paste your Access-Token in the totalvoice_odoo module configuration
page and then save.

.. code-block:: xml

    API-KEY: your access-token
    API-URL: api.totalvoice.com.br

Now, in the Odoo Configuration page, go in
'Technical/Automation/Webhook' and search for the TotalVoice
consumer_name. Insert your **webhook-url** in the field **IP or Network
Address**, overriding the existing one.

.. code-block:: xml

    http://prod.yourcompany.odoo.com.br/webhook/totalvoice

Webhook Usage
=============

In order to use the Webhook event handler, you must create a new class in
your module, inheriting 'totalvoice.base'.

In this class, you should be able to add new **subjects** to the subject
field declared in the totalvoice.base. The subject name will be used to
form the method name which will be called.

Example of methods the webhook will call:

.. code-block:: xml

    def confirm_operation_yes(self, *args)
    def confirm_operation_no(self, *args)

    def assign_task_yes(self, *args)
    def assign_task_no(self, *args)

Where **confirm_operation** and **assign_task** are names of new subjects,
 **yes** and **no** are possible answers to the sent SMS and **\*args** is
 the text after the first word in the SMS answer.

Below is a clearer example of how to override the totalvoice.base class

.. code-block:: python

    SUBJECT_SELECTION = [
        ('assign_task', 'Assign a Task'),
        ('cancel_assign', "Cancel an Assigned Task"),
    ]
    class TotalVoiceBase(models.Model):
        _inherit = 'totalvoice.base'

        healthprofessional_id = fields.Many2one(
            string="Health Professional",
            comodel_name='pontomedical.healthprofessional',
            ondelete='cascade',
        )

        subject = fields.Selection(
            selection_add=SUBJECT_SELECTION,
        )

        @api.multi
        def assign_task_0(self, *args):
            self.ensure_one()
            self.healthprofessional_id.confirm_appointments()

        @api.multi
        def assign_task_1(self, *args):
            self.ensure_one()
            self.healthprofessional_id.confirm_appointments(appointments=None)

        @api.multi
        def cancel_assign_YES(self, *args):
            self.ensure_one()
            self.healthprofessional_id.cancel_assign(attach_reason=args)


So, if the following SMS is sent to the user with the subject
**cancel_assign**:

.. code-block:: xml

    Do you want to cancel the assign? Type YES if you do want, following by
     your reasons.

The user can answer that with, for example:

.. code-block:: xml

    YES. Because tomorrow is my son's birthday.

In this situation, the method **cancel_assign_YES** will be called, and
**\*args*** will be filled with the string 'Because tomorrow is my son's
birthday.'.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/KMEE/web/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.


Contributors
------------

* Hugo Uchoas Borges <hugo.borges@kmee.com.br>
