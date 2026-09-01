from odoo import models, api, fields
from odoo.http import request
from werkzeug.utils import redirect

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _dispatch(cls, endpoint):
        if hasattr(request, 'httprequest') and request.httprequest:
            path = request.httprequest.path
            accept_header = request.httprequest.headers.get('Accept', '')
            
            # Catch HTML navigations across all backend routes (/web, /odoo, /action)
            is_html = 'text/html' in accept_header
            is_backend = path.startswith('/web') or path.startswith('/odoo') or 'action' in path
            is_exempt = '/web/login' in path or '/web/session' in path or '/my/' in path
            
            if is_backend and not is_exempt and is_html:
                env = request.env
                user = env.user
                
                # STRICT LOCKOUT: Only System (1) and Vast-Solutions Tech Admin (2) are immune
                if user and user.id not in [1, 2]:
                    partner = user.partner_id.commercial_partner_id
                    sub = env['sale.order'].sudo().search([
                        ('partner_id', 'child_of', partner.id),
                        ('is_subscription', '=', True),
                        ('subscription_state', '=', 'past_due')
                    ], limit=1, order='id desc')
                    
                    if sub:
                        return redirect('/my/invoices')
                        
        return super(IrHttp, cls)._dispatch(endpoint)

    def session_info(self):
        result = super(IrHttp, self).session_info()
        user = self.env.user
        
        if user and user.id != 1: 
            partner = user.partner_id.commercial_partner_id
            sub = self.env['sale.order'].sudo().search([
                ('partner_id', 'child_of', partner.id),
                ('is_subscription', '=', True),
                ('subscription_state', 'in', ['active', 'trial'])
            ], limit=1, order='next_invoice_date asc')
            
            if sub and sub.next_invoice_date:
                today = fields.Date.context_today(self)
                delta = (sub.next_invoice_date - today).days
                if delta >= 0 and delta <= 3:
                    result['vast_sub_warning_days'] = delta
                    result['vast_sub_warning'] = True
        return result