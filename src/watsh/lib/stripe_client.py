# import aiohttp
# from aiohttp import BasicAuth
# Create user on stripe
    # TODO: put in transaction
    # stripe_secret_key = "sk_test_51Nf7hXGUlugIQZAoCjL4Pt5Zlx6aMyLZoPDYzMdnqKCBW7U35t5OEE7WwHAxyzhMDUsRpLKZE764zbAscrvc9WEI00XJsuRpWF"
    # auth = BasicAuth(login=stripe_secret_key, password="")
    # data = {'email': email_address}
    # async with aiohttp.ClientSession() as session:
    #     async with session.post('https://api.stripe.com/v1/customers', auth=auth, data=data) as resp:
    #         if not resp.status == 200:
    #             raise Exception('Not good')
            
    # Get stripe customer id
    # curl -G https://api.stripe.com/v1/customers/search \
    #   -u "sk_test_51Nf7hXGUlugIQZAoCjL4Pt5Zlx6aMyLZoPDYzMdnqKCBW7U35t5OEE7WwHAxyzhMDUsRpLKZE764zbAscrvc9WEI00XJsuRpWF:" \
    #   --data-urlencode query="name:'Jane Doe' AND metadata['foo']:'bar'"

    # Customer portal session
    # curl https://api.stripe.com/v1/billing_portal/sessions \
    #   -u "sk_test_51Nf7hXGUlugIQZAoCjL4Pt5Zlx6aMyLZoPDYzMdnqKCBW7U35t5OEE7WwHAxyzhMDUsRpLKZE764zbAscrvc9WEI00XJsuRpWF:" \
    #   -d customer=cus_NciAYcXfLnqBoz \
    #   --data-urlencode return_url="https://example.com/account"

    # Create subscription
    # curl https://api.stripe.com/v1/subscriptions \
    # -u "sk_test_51Nf7hXGUlugIQZAoCjL4Pt5Zlx6aMyLZoPDYzMdnqKCBW7U35t5OEE7WwHAxyzhMDUsRpLKZE764zbAscrvc9WEI00XJsuRpWF:" \
    # -d customer=cus_Na6dX7aXxi11N4 \
    # -d "items[0][price]"=price_1MowQULkdIwHu7ixraBm864M
    # trial_end

    # Get subscription status
    # curl -G https://api.stripe.com/v1/subscriptions/search \
    # -u "sk_test_51Nf7hXGUlugIQZAoCjL4Pt5Zlx6aMyLZoPDYzMdnqKCBW7U35t5OEE7WwHAxyzhMDUsRpLKZE764zbAscrvc9WEI00XJsuRpWF:" \
    # --data-urlencode query="customer:'cus_id'"
