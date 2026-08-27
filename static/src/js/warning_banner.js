/** @odoo-module **/

import { Component, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { session } from "@web/session";

export class VastSubWarningBanner extends Component {
    setup() {
        this.showWarning = false;
        this.days = 0;

        onMounted(() => {
            if (session.vast_sub_warning && !window.sessionStorage.getItem('vast_sub_warned')) {
                this.days = session.vast_sub_warning_days;
                this.showWarning = true;
                window.sessionStorage.setItem('vast_sub_warned', 'true');
            }
        });
    }

    dismiss() {
        this.showWarning = false;
    }
}

VastSubWarningBanner.template = "Odoo_Custom_Subscription.WarningBanner";

registry.category("main_components").add("VastSubWarningBanner", {
    Component: VastSubWarningBanner,
});