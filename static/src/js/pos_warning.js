/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/services/pos_store";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(PosStore.prototype, {
    async setup() {
        await super.setup(...arguments);

        const session = this.env.services.session;
        if (session && session.vast_sub_warning && !window.sessionStorage.getItem('vast_sub_warned_pos')) {
            window.sessionStorage.setItem('vast_sub_warned_pos', 'true');

            // Show popup gracefully after standard initialization
            setTimeout(() => {
                this.env.services.dialog.add(ConfirmationDialog, {
                    title: 'Subscription Renewal Notice',
                    body: `Your subscription renews in ${session.vast_sub_warning_days} days. Please ensure payment methods are up to date.`,
                });
            }, 3000);
        }
    }
});