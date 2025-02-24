/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { SMSSignerDialog } from "@sign/dialogs/sms_signer_dialog";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";


patch(SMSSignerDialog.prototype, {
    sendSMS(phoneNumber) {
        console.log("sendSMS - Custom Override");
        this.state.sendingSMS = true;
        const route = `/sign/send-sms/${this.signInfo.get("documentId")}/${this.signInfo.get(
            "signRequestItemToken"
        )}/${phoneNumber}`;

        this.rpc(route)
            .then((response) => {
                console.log("then - Response received:", response);
                if (response.success) {
                    console.log("success");
                    this.handleSendSMSSuccess();
                } else {
                    console.log("else - Error from backend:", response.error);
                    this.handleSMSError(response.error || "Unknown backend error.");
                }
            })
            .catch((e) => {
                console.log("catch - Exception:", e);
                this.handleSMSError(e.message || "An unexpected error occurred.");
            });
    },

    handleSMSError(errorMessage) {
        console.log("handleSMSError:", errorMessage);
        console.log("this.dialog:", this.dialog);
        this.state.sendingSMS = false;
        this.dialog.add(AlertDialog, {
            title: _t("Error"),
            body: errorMessage,
        });
    }
    
});
