{
    'name': 'Bill OCR',
    'version': '1.0',
    'category': 'Accounting',
    'description': """
        This module provides the ability to extract text from a PDF bill using OCR technology.
    """,
    'author': 'Your Name',
    'website': 'https://www.example.com',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/bills.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
