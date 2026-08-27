{
    'name': 'Vast Subscriptions',
    'version': '19.0.1.0.0',
    'summary': 'Automated Recurring Billing and Subscription Engine',
    'description': """
Vast Subscriptions
==================
A custom module that provides a streamlined, fully automated recurring billing and subscription engine with a 14-day free trial.
    """,
    'category': 'Sales/Subscriptions',
    'author': 'Antigravity',
    'depends': ['sale_management', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/subscription_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
