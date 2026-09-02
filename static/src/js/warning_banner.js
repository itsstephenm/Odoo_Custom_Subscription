/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { session } from "@web/session";

export class VastSubWarningBanner extends Component {
    setup() {
        this.state = useState({
            showWarning: false,
            days: 0,
        });

        onMounted(() => {
            const path = window.location.pathname;
            const isLogin = path === '/web/login';
            const isPos = path.includes('/pos/ui');

            console.log("=== 🔍 VastSubWarningBanner Check ===", {
                path,
                vast_sub_warning: session.vast_sub_warning,
                days: session.vast_sub_warning_days
            });

            if (session.vast_sub_warning && !isLogin && !isPos) {
                this.state.days = session.vast_sub_warning_days || 3;
                this.state.showWarning = true;
            }
        });
    }

    dismiss() {
        this.state.showWarning = false;
    }
}

VastSubWarningBanner.template = "Odoo_Custom_Subscription.WarningBanner";

registry.category("main_components").add("VastSubWarningBanner", {
    Component: VastSubWarningBanner,
});