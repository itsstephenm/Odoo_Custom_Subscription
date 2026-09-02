/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { session } from "@web/session";

export class VastSubWarningBanner extends Component {
    static template = "Odoo_Custom_Subscription.WarningBanner";
    static props = {};

    setup() {
        this.state = useState({
            showWarning: false,
            days: 0,
        });

        try {
            const path = window.location.pathname || "";
            const isLogin = path.includes('/web/login');
            const isPos = path.includes('/pos/ui');

            if (session && session.vast_sub_warning && !isLogin && !isPos) {
                this.state.days = session.vast_sub_warning_days || 3;
                this.state.showWarning = true;
            }
        } catch (e) {
            console.error("Error initializing VastSubWarningBanner:", e);
        }
    }

    dismiss() {
        this.state.showWarning = false;
    }
}

registry.category("main_components").add("VastSubWarningBanner", {
    Component: VastSubWarningBanner,
});