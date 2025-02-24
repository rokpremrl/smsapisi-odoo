from odoo import http, _
from odoo.http import request
import logging
from odoo.addons.sign.controllers.main import Sign
from odoo.addons.iap.tools import iap_tools

_logger = logging.getLogger(__name__)

class SignControllerOverride(Sign):

    # overriden to change response to include error message
    @http.route('/sign/send-sms/<int:request_id>/<token>/<phone_number>', type='json', auth='public')
    def send_sms(self, request_id, token, phone_number):
        request_item = request.env['sign.request.item'].sudo().search([
            ('sign_request_id', '=', request_id),
            ('access_token', '=', token),
            ('state', '=', 'sent')
        ], limit=1)

        if not request_item:
            _logger.warning("No valid request item found.")
            return {"success": False, "error": "Invalid request."}

        if request_item.role_id.auth_method == 'sms':
            request_item.sms_number = phone_number
            try:
                request_item._send_sms()
                return {"success": True}
            except iap_tools.InsufficientCreditError:
                _logger.warning("Unable to send SMS: No more credits.")
                request_item.sign_request_id.activity_schedule(
                    'mail.mail_activity_data_todo',
                    note=_("%s couldn't sign the document due to insufficient credit.", request_item.partner_id.display_name),
                    user_id=request_item.sign_request_id.create_uid.id
                )
                return {"success": False, "error": "Insufficient credit to send SMS. Please top up."}
            except Exception as e:
                _logger.error(f"🔥 Unexpected error in send_sms: {e}")
                return {"success": False, "error": f"Error sending SMS: {str(e)}"}

        return {"success": True}
