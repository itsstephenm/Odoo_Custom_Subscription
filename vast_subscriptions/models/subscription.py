from odoo import api, fields, models, _
import datetime
from dateutil.relativedelta import relativedelta

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_subscription_product = fields.Boolean(
        string='Is Subscription Product',
        default=False,
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
                order.message_post(body=_("Subscription Trial Started. Ends on %s", order.trial_end_date))
        return res

    @api.model
    def _cron_process_subscriptions(self):
        today = fields.Date.context_today(self)
        
        # 1. Past Due Evaluator
        active_subs = self.search([('is_subscription', '=', True), ('subscription_state', '=', 'active')])
        for sub in active_subs:
            unpaid_invoices = sub.invoice_ids.filtered(
                lambda inv: inv.state == 'posted' and inv.payment_state in ('not_paid', 'partial') and inv.invoice_date_due and inv.invoice_date_due < today
            )
            if unpaid_invoices:
                sub.subscription_state = 'past_due'
                sub.message_post(body=_("Subscription marked Past Due because of unpaid invoices."))

        past_due_subs = self.search([('is_subscription', '=', True), ('subscription_state', '=', 'past_due')])
        for sub in past_due_subs:
            unpaid_invoices = sub.invoice_ids.filtered(
                lambda inv: inv.state == 'posted' and inv.payment_state in ('not_paid', 'partial') and inv.invoice_date_due and inv.invoice_date_due < today
            )
            if not unpaid_invoices:
                sub.subscription_state = 'active'
                sub.message_post(body=_("Outstanding invoices paid. Subscription restored to Active."))

        # 2. Billing Generation
        subscriptions = self.search([
            ('is_subscription', '=', True),
            ('subscription_state', 'in', ['trial', 'active']),
            ('next_invoice_date', '<=', today)
        ])

        for sub in subscriptions:
            try:
                if sub.subscription_state == 'trial':
                    sub.subscription_state = 'active'
                    sub.message_post(body=_("Subscription trial ended. State changed to Active."))

                invoice_vals = sub._prepare_invoice()
                invoice = self.env['account.move'].create(invoice_vals)
                
                for line in sub.order_line:
                    line._set_external_taxes(line.price_unit, invoice)
                    invoice_line_vals = line._prepare_invoice_line()
                    invoice.write({'invoice_line_ids': [(0, 0, invoice_line_vals)]})

                if invoice:
                    invoice.action_post()
                    template = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
                    if template:
                        template.send_mail(invoice.id, force_send=True)

                if sub.recurring_interval == 'monthly':
                    sub.next_invoice_date = today + relativedelta(months=1)
                elif sub.recurring_interval == 'yearly':
                    sub.next_invoice_date = today + relativedelta(years=1)

            except Exception as e:
                sub.message_post(body=_("Error generating recurring invoice: %s", str(e)))
