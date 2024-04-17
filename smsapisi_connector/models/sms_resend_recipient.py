# -*- coding: utf-8 -*-

from odoo import fields, models

class SmsResendRecipient(models.TransientModel):
    _inherit = "sms.resend.recipient"

    sms_api_error = fields.Char(related="notification_id.sms_api_error")