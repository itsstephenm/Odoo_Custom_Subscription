/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/services/pos_store";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { session } from "@web/session";

// TEST 1: Did the file load into the browser?
console.log("=== 🔍 POS WARNING SCRIPT LOADED (Disabled per requirements) ===");

patch(PosStore.prototype, {
    async setup() {
        await super.setup(...arguments);
        // Popup logic removed: Warning banner must not appear inside the POS interface.
    }
});