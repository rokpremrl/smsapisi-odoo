# -*- coding: utf-8 -*-

from odoo import fields, models

class MailNotification(models.Model):
    _inherit = "mail.notification"

    sms_api_error = fields.Char(related="sms_id.sms_api_error")