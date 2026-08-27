{
    'name': 'Vast Subscriptions',
    'version': '19.0.2.0.0',
    'summary': 'Automated Recurring Billing, SaaS Paywall & 14-Day Trial',
    'description': """
Vast Subscriptions (v2)
=======================
Advanced SaaS paywall with automated billing, 3-day proactive renewal warnings (Web and POS), and hard paywall lockouts for past-due accounts.
    """,
    'category': 'Sales/Subscriptions',
    'author': 'Antigravity',
    'depends': ['sale_management', 'account', 'point_of_sale', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/subscription_views.xml',
        'views/paywall_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'vast_subscriptions/static/src/js/warning_banner.js',
            'vast_subscriptions/static/src/xml/warning_banner.xml',
        ],
        'point_of_sale._assets_pos': [
            'vast_subscriptions/static/src/js/pos_warning.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
