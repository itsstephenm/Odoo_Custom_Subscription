{
    'name': 'Vast Subscriptions',
    'version': '19.0.1.0.0',
    'summary': 'Automated Recurring Billing and Subscription Engine with SaaS Paywall',
    'description': """
Vast Subscriptions
==================
A custom module that provides a streamlined, fully automated recurring 
billing and subscription engine with a 14-day free trial, proactive 3-day 
warnings, and a hard SaaS paywall.
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
            'Odoo_Custom_Subscription/static/src/js/warning_banner.js',
            'Odoo_Custom_Subscription/static/src/xml/warning_banner.xml',
        ],
        'point_of_sale._assets_pos': [
            'Odoo_Custom_Subscription/static/src/js/pos_warning.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}