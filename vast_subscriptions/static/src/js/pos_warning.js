/** @odoo-module **/

import { PosGlobalState } from "@point_of_sale/app/store/pos_global_state";
import { patch } from "@web/core/utils/patch";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";

patch(PosGlobalState.prototype, {
    async setup() {
        await super.setup(...arguments);
        
        const session = this.env.services.session;
        if (session && session.vast_sub_warning && !window.sessionStorage.getItem('vast_sub_warned_pos')) {
            window.sessionStorage.setItem('vast_sub_warned_pos', 'true');
            
            // Show popup gracefully after standard initialization
            setTimeout(() => {
                this.env.services.popup.add(ConfirmPopup, {
                    title: 'Subscription Renewal Notice',
                    body: `Your subscription renews in ${session.vast_sub_warning_days} days. Please ensure payment methods are up to date.`,
                });
            }, 3000);
        }
    }
});
