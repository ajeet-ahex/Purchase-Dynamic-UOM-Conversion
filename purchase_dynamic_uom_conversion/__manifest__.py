# __manifest__.py

{
    'name': 'Purchase Dynamic UoM Conversion',
    'version': '19.0.0.1',
    'category': 'Purchases',
    'summary': 'Dynamic conversion ratio for purchase pricing and dynamic Unit of Measure handling.',
    'author': 'Ahex Technologies',
    'website': 'https://www.ahex.co',
    'sequence': 10,
    'description': """
        Purchase Dynamic UoM Conversion allows you to define a Purchase UoM different from the base Stock UoM with automated conversion ratios and pricing.
    """,
    'depends': ['purchase', 'product'],
    'data': [
        'reports/report_purchase_order_inherit.xml',
        'reports/report_purchase_quotation_inherit.xml',
        'views/product_views.xml',
        'views/purchase_views.xml',
    ],
    'license': 'OPL-1',
    'application': False,
    'installable': True,
    'auto_install': False,
}