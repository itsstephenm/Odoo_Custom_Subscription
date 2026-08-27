from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import datetime

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_subscription_product = fields.Boolean(
        string='Is Subscription Product',
        default=False,
        help="Check this if the product is a subscription that triggers recurring billing."
    )

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_subscription = fields.Boolean(
        string='Is Subscription',
        compute='_compute_is_subscription',
        store=True
    )
    subscription_state = fields.Selection([
        ('draft', 'Draft'),
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('cancelled', 'Cancelled')
    ], string='Subscription Status', default='draft', copy=False, tracking=True)

    trial_start_date = fields.Date(string='Trial Start Date', copy=False)
    trial_end_date = fields.Date(string='Trial End Date', copy=False)
    next_invoice_date = fields.Date(string='Next Invoice Date', copy=False, tracking=True)
    recurring_interval = fields.Selection([
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
    ], string='Recurring Interval', default='monthly')

    @api.depends('order_line.product_id.is_subscription_product')
    def _compute_is_subscription(self):
        for order in self:
            order.is_subscription = any(line.product_id.is_subscription_product for line in order.order_line)

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.is_subscription:
                order.trial_start_date = fields.Date.context_today(order)
                order.trial_end_date = order.trial_start_date + datetime.timedelta(days=14)
                order.next_invoice_date = order.trial_end_date + datetime.timedelta(days=1)
                order.subscription_state = 'trial'
                order.message_post(body=_("Subscription Trial Started. Trial ends on %s", order.trial_end_date))
        return res

    @api.model
    def _cron_process_subscriptions(self):
        today = fields.Date.context_today(self)
        subscriptions = self.search([
            ('is_subscription', '=', True),
            ('subscription_state', 'in', ['trial', 'active']),
            ('next_invoice_date', '<=', today)
        ])

        for sub in subscriptions:
            try:
                # If it's trial and next invoice date is reached, trial is over, it becomes active.
                if sub.subscription_state == 'trial':
                    sub.subscription_state = 'active'
                    sub.message_post(body=_("Subscription trial ended. State changed to Active."))

                # Create invoice programmatically
                invoice_vals = sub._prepare_invoice()
                invoice = self.env['account.move'].create(invoice_vals)
                
                # Add invoice lines based on sale order lines
                for line in sub.order_line:
                    line._set_external_taxes(line.price_unit, invoice)
                    invoice_line_vals = line._prepare_invoice_line()
                    # Ensure price unit is correctly updated or other specifics handled
                    invoice.write({'invoice_line_ids': [(0, 0, invoice_line_vals)]})

                if invoice:
                    invoice.action_post()
                    
                    # Send Email
                    template = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
                    if template:
                        template.send_mail(invoice.id, force_send=True)
                        sub.message_post(body=_("Recurring invoice %s created and sent.", invoice.name))
                    else:
                        sub.message_post(body=_("Recurring invoice %s created but email template not found.", invoice.name))

                # Update next invoice date
                if sub.recurring_interval == 'monthly':
                    sub.next_invoice_date = today + relativedelta(months=1)
                elif sub.recurring_interval == 'yearly':
                    sub.next_invoice_date = today + relativedelta(years=1)

            except Exception as e:
                sub.message_post(body=_("Error generating recurring invoice: %s", str(e)))
                sub.subscription_state = 'past_due'
