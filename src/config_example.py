# ------------------------------ MAIN CONFIGS ---------------------------------
# is displayed in the header of the site
ACCOUNT_NAME = 'YOUR ACCOUNT NAME'

DOMAIN = 'https://yourdomoian.com/'

SUPPORT_EMAIL = 'youremail@yourprovider.com'
PRODUCER_DISPLAY_NAME = 'Your Name that will be shown to your customers'

PHONE_NUMBER = '00-00000-0000'

# --------------------------- CHECKOUT CONFIGS --------------------------------

#  Payment Options:
#  "2" for Only Credit Card
#  "4" for Credit Card and Pix
#  "1" for Credit Card and Billet
#  "3" for Credit Card, Billet and Pix

PAYMENT_OPTION = "3"

#  Payment Times:
#  "1" for 1x, "2" for 2x, etc. Maximun is 12.
PAYMENT_TIMES = "12"

# Set 0 to not use Exit Popup
EXIT_POPUP_DISCOUNT = 0

EXIT_POPUP_TEXTS = {
    'title': ('PARABÉNS, VOCÊ ACABOU DE GANHAR '
              f'{EXIT_POPUP_DISCOUNT}% DE DESCONTO...'),
    'button_text': 'QUERO APROVEITAR ESSA CONDIÇÃO EXCLUSIVA!',
    'additional_text': '''

Essa condição não vai se repetir! ESSA É SUA CHANCE!'''
}

# Set '' or None to not use Whatsapp on Checkout
CHECKOUT_PHONE_NUMBER = '00-00000-0000'

# ----------------------- ORDERBUMP|UPSELL CONFIGS ----------------------------

# name for a additional plan, leave empty to not create one
ADDITIONAL_PLAN = 'OrderBump'

# -----------------------------------------------------------------------------

COURSES = {
    'yourcourse': {'base_price': 47, 'additional': 27},
    'yourcourse2': {'base_price': 47, 'additional': 27},
}
