from odoo import fields, models, _
from odoo.exceptions import UserError, ValidationError

class SignRequest(models.Model):
    _inherit = "sign.request.item"

    # copy of the original function with added 'raise_exception=True'
    def _send_sms(self):
        self._reset_sms_token()
        sms_values = [{'body': _('Your confirmation code is %s', rec.sms_token), 'number': rec.sms_number} for rec in self]
        self.env['sms.sms'].sudo().create(sms_values).send(raise_exception=True)