from odoo import models, api, fields
from odoo.http import request
from werkzeug.utils import redirect
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _dispatch(cls, endpoint):
        if hasattr(request, 'httprequest') and request.httprequest:
            path = request.httprequest.path
            accept_header = request.httprequest.headers.get('Accept', '')
            
            is_html = 'text/html' in accept_header
            
            # Strictly target backend workspace routes (like /odoo/action-...) without trapping portal/dataset calls
            is_backend = path.startswith('/odoo') or 'action' in path
            
            is_exempt = (
                path.startswith('/web/login') or 
                path.startswith('/web/session') or 
                path.startswith('/web/assets') or 
                path.startswith('/web/static') or 
                path.startswith('/web/image') or 
                path.startswith('/web/content') or 
                path.startswith('/web/bundle') or 
                path.startswith('/website/translations') or 
                path.startswith('/payment') or 
                path.startswith('/my')
            )
            
            if is_backend and not is_exempt:
                uid = request.session.uid
                
                if uid and uid != 1:
                    user = request.env['res.users'].sudo().browse(uid)
                    partner = user.partner_id.commercial_partner_id
                    
                    sub = request.env['sale.order'].sudo().search([
                        ('partner_id', 'child_of', partner.id),
                        ('subscription_state', '=', 'past_due')
                    ], limit=1)
                    
                    if sub:
                        _logger.info(f"LOCKOUT TRIGGERED for User ID {uid} on path {path}")
                        if is_html:
                            return redirect('/my/invoices')
                        else:
                            raise AccessError("SYSTEM LOCKOUT: Your subscription is past due. Please navigate to the portal to pay your outstanding invoices.")
                        
        return super(IrHttp, cls)._dispatch(endpoint)

    def session_info(self):
        result = super(IrHttp, self).session_info()
        user = self.env.user
        
        if user and user.id != 1: 
            partner = user.partner_id.commercial_partner_id
            sub = self.env['sale.order'].sudo().search([
                ('partner_id', 'child_of', partner.id),
                ('subscription_state', 'in', ['active', 'trial'])
            ], limit=1, order='next_invoice_date asc')
            
            if sub and sub.next_invoice_date:
                today = fields.Date.context_today(self)
                delta = (sub.next_invoice_date - today).days
                if delta >= 0 and delta <= 3:
                    result['vast_sub_warning_days'] = delta
                    result['vast_sub_warning'] = True
        return result