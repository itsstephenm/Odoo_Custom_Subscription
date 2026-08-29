/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/services/pos_store";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { session } from "@web/session";

// TEST 1: Did the file load into the browser?
console.log("=== 🔍 POS WARNING SCRIPT LOADED ===");

patch(PosStore.prototype, {
    async setup() {
        // TEST 2: Is the POS store patch executing?
        console.log("=== 🔍 POS SETUP PATCH INITIATED ===");

        await super.setup(...arguments);

        // TEST 3: What data did we actually get from Python?
        console.log("🔍 Session Warning Flag:", session.vast_sub_warning);
        console.log("🔍 Session Days Remaining:", session.vast_sub_warning_days);
        console.log("🔍 SessionStorage Cached Flag:", window.sessionStorage.getItem('vast_sub_warned_pos'));

        if (session.vast_sub_warning) {
            if (!window.sessionStorage.getItem('vast_sub_warned_pos')) {
                console.log("=== ✅ CONDITION MET: ATTEMPTING TO SHOW POPUP ===");

                window.sessionStorage.setItem('vast_sub_warned_pos', 'true');

                setTimeout(() => {
                    console.log("=== 🚀 SPAWNING DIALOG NOW ===");
                    this.env.services.dialog.add(ConfirmationDialog, {
                        title: 'Subscription Renewal Notice',
                        body: `Your subscription renews in ${session.vast_sub_warning_days} days. Please ensure payment methods are up to date.`,
                    });
                }, 3000);
            } else {
                console.log("=== 🛑 SKIPPED: ALREADY WARNED IN THIS BROWSER SESSION ===");
            }
        } else {
            console.log("=== 🛑 SKIPPED: WARNING IS FALSE OR UNDEFINED ===");
        }
    }
});