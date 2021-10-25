from .services import Paystack


def card_post_save(sender, instance, created, **kwargs):
    if not created:
        return

    # # Refund user after saving card details.
    paystack = Paystack()
    paystack.create_refund(instance.reference)
