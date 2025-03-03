# -*- coding: utf-8 -*-
{
    'name': "SMSapi.si Connector",
    'summary': "Send SMS with SMSapi.si",
    'author': "Guru d.o.o.",
    'website': "https://www.guru.si/",
    'license': 'LGPL-3',
    'category': 'Technical',
    'version': '17.0.1.2.0',
    'depends': ['base', "sms", "iap", "phone_validation", "sign"],
    'external_dependencies': {
        'python': ['phonenumbers', 'requests']
    },
    'data': [
        'data/iap_account_data.xml',
        'data/ir_cron.xml',
        'views/iap_account.xml',
        'views/sms_sms.xml',
        'views/sms_resend.xml'
    ],
    'images': ['static/description/smsapi_banner.png'],
    "assets": {
        "web.assets_backend": [
            "smsapisi_connector/static/src/js/sms_signer_dialog.js",
        ],
        "web.assets_frontend": [
            "smsapisi_connector/static/src/js/sms_signer_dialog.js",
        ],
        "sign.assets_public_sign": [
            "smsapisi_connector/static/src/js/sms_signer_dialog.js",
        ],
    },
}
