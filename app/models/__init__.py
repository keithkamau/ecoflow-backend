# __init__.py
# import all models here so SQLAlchemy can find them
# when we call Base.metadata.create_all() in main.py

from app.models.offer import Offer, OfferStatus
from app.models.transaction import Transaction, TransactionStatus
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.message import Message