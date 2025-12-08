# from fastapi import APIRouter, Depends, HTTPException
# from db_connection import get_db
# from models import PaymentRequest

# payment_router = APIRouter(prefix="/payment", tags=["Payment"])

# @payment_router.post("/process")
# async def process_payment(request: PaymentRequest, db=Depends(get_db)):
#     transaction_id = request.transaction_id
#     customer_id = request.customer_id
#     # get balance from customer account

#     try:
#         with db.cursor() as cursor:
#             # Check Transaction exists
#             cursor.execute("SELECT * FROM `Transaction` WHERE TransactionID=%s", (transaction_id,))
#             transaction = cursor.fetchone()
#             if not transaction:
#                 raise HTTPException(status_code=404, detail="Transaction not found")

#             if transaction["CustomerID"] != customer_id:
#                 raise HTTPException(status_code=400, detail="Transaction does not belong to the customer")

#             if transaction["PaidAt"] is not None:
#                 raise HTTPException(status_code=400, detail="Transaction is already paid")

#             total_price = transaction["TotalPrice"]

#             # Check Customer balance
#             cursor.execute("SELECT Balance FROM Customer WHERE CustomerID=%s", (customer_id,))
#             customer = cursor.fetchone()
#             if not customer:
#                 raise HTTPException(status_code=404, detail="Customer not found")

#             if customer["Balance"] < total_price:
#                 raise HTTPException(status_code=400, detail="Insufficient balance")

#             # Deduct balance and mark transaction as paid
#             new_balance = customer["Balance"] - total_price
#             cursor.execute("UPDATE Customer SET Balance=%s WHERE CustomerID=%s", (new_balance, customer_id))
#             cursor.execute('UPDATE `Transaction` SET PaidAt=NOW(), Status = "Paid" WHERE TransactionID=%s', (transaction_id,))
#             db.commit()

#             return {"message": "Payment processed successfully", "new_balance": new_balance}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
    