# ------------------------------ MAIN CONFIGS ---------------------------------
# is displayed in the header of the site
ACCOUNT_NAME = 'YOUR ACCOUNT NAME'

DOMAIN = 'https://yourdomoian.com/'

SUPPORT_EMAIL = 'youremail@yourprovider.com'
PRODUCER_DISPLAY_NAME = 'Your Name that will be shown to your customers'

SUPPORT_NUMBER_ON_FIRST_LESSON = True
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

# ----------------------- ORDERBUMP|UPSELL CONFIGS ----------------------------

# name for a additional plan, leave empty to not create one
ADDITIONAL_PLAN = 'OrderBump'

# -----------------------------------------------------------------------------

COURSES = {
    'yourcourse': {'base_price': 47, 'additional': 27},
    'yourcourse2': {'base_price': 47, 'additional': 27},
}
