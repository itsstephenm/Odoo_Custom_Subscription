from odoo import http
from odoo.http import request

class SubscriptionPaywall(http.Controller):
    @http.route('/subscription/suspended', type='http', auth='user', website=True)
    def subscription_suspended(self, **kwargs):
        return request.render('vast_subscriptions.paywall_page', {})
