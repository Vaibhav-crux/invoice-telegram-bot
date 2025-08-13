from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Define invoice options
INVOICE_OPTIONS = [
    {"display": "Proforma Invoice", "callback_data": "proforma_invoice"},
    {"display": "Sales Invoice", "callback_data": "sales_invoice"},
    {"display": "Overdue Invoice", "callback_data": "overdue_invoice"},
    {"display": "Retainer Invoice", "callback_data": "retainer_invoice"},
]

def get_invoice_keyboard():
    """
    Create an inline keyboard with invoice options for Telegram.
    
    Returns:
        InlineKeyboardMarkup: Telegram inline keyboard with invoice options.
    """
    keyboard = [
        [
            InlineKeyboardButton(option["display"], callback_data=option["callback_data"])
            for option in INVOICE_OPTIONS[i:i+2]
        ]
        for i in range(0, len(INVOICE_OPTIONS), 2)
    ]
    return InlineKeyboardMarkup(keyboard)