# mock_payment.py
# simulates M-Pesa payment responses for MVP
# when we integrate real Daraja API, we replace these functions

import uuid

def simulate_mpesa_payment(phone: str, amount: float):
    # pretend we called M-Pesa and got a success response back
    return {
        "success": True,
        "reference": f"MP-{uuid.uuid4().hex[:8].upper()}",
        "message": f"Payment of KES {amount} received from {phone}",
        "amount": amount
    }

def simulate_card_payment(card_last4: str, amount: float):
    # pretend we processed a card payment
    return {
        "success": True,
        "reference": f"CARD-{uuid.uuid4().hex[:8].upper()}",
        "message": f"Card ending {card_last4} charged KES {amount}",
        "amount": amount
    }