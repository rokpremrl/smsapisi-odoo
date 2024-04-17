# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.addons.phone_validation.tools import phone_validation
import logging
import requests

_logger = logging.getLogger(__name__)

SMS_API_SI_URL = "https://www.smsapi.si/poslji-sms"

class Sms(models.Model):
    _inherit = "sms.sms"

    sms_api_error = fields.Char()
    
    def _prepare_sms_api_si_params(self, iap_account):
        self.ensure_one()

        parsed_number = phone_validation.phone_parse(self.number, None)

        params = {
            "un": iap_account.sms_api_username,
            "ps": iap_account.sms_api_password,
            "from": iap_account.sms_api_from,
            "to": self.number,
            "cc": parsed_number.country_code,
            "m": self.body,
            'unicode': '1',
        }

        if iap_account.sms_api_use_sid and iap_account.sms_api_sname:
            params['sid'] = '1'
            params['sname'] = iap_account.sms_api_sname

        return params

    def _send(self, unlink_failed=False, unlink_sent=True, raise_exception=False):
        """ This method tries to send SMS after checking the number (presence and
        formatting). """

        if self._is_sent_with_sms_api():
            # copied from super and modified
            try:
                result = self._send_sms_with_sms_api_si()
                iap_results = [{'res_id': sms.id, 'state': result} for sms in self]
                # iap_results format:
                # :return: return of /iap/sms/1/send controller which is a list of dict [{
                #     'res_id': integer: ID of sms.sms,
                #     'state':  string: 'insufficient_credit' or 'wrong_number_format' or 'success',
                #     'credit': integer: number of credits spent to send this SMS,
                # }]
            except Exception as e:
                _logger.warning('Sent batch %s SMS: %s: failed with exception %s', len(self.ids), self.ids, e)
                if raise_exception:
                    raise
                self._postprocess_iap_sent_sms(
                    [{'res_id': sms.id, 'state': 'server_error'} for sms in self],
                    unlink_failed=unlink_failed, unlink_sent=unlink_sent)
            else:
                _logger.info('Send batch %s SMS: %s: gave %s', len(self.ids), self.ids, iap_results)
                self._postprocess_iap_sent_sms(iap_results, unlink_failed=unlink_failed, unlink_sent=unlink_sent)
        else:
            return super()._send(unlink_failed=unlink_failed, unlink_sent=unlink_sent, raise_exception=raise_exception)
        

    def _is_sent_with_sms_api(self):
        return self.env['iap.account']._get_sms_account().provider == "sms_api_si"

    def _send_sms_with_sms_api_si(self):
        self.ensure_one()
        # Try to return same error code like odoo
        # list is here: self.IAP_TO_SMS_STATE
        if not self.number:
           return "wrong_number_format"

        iap_account_sms = self.env['iap.account']._get_sms_account()

        # return format: ID##SMS_PRICE##FROM##TO --- example: 123##0.03##040123456##040654321
        # in case of error: -1##ERROR##FROM##TO
        response = requests.get(
            SMS_API_SI_URL,
            params=self._prepare_sms_api_si_params(iap_account_sms),
        )

        response_content = response.content.decode('utf-8')
        _logger.debug(f"smsapi.si responded with: {response_content}")

        if response_content[:2] != "-1":
            _logger.info("SMS sent successfully")
            return "success"
    
        error_code = response_content.split('##')[1]
        error_msg = self.env['iap.account'].get_sms_api_si_error(error_code)
        _logger.warning(f"Failed to send SMS: {error_msg}")

        self.sms_api_error = error_msg
        return "server_error"

    def _split_batch(self):
        if self._is_sent_with_sms_api():
            # No batch with smsapi.si
            for record in self:
                yield [record.id]
        else:
            yield from super()._split_batch()
