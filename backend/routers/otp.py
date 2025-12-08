from fastapi import APIRouter, Depends, HTTPException
from services.otp_service import generate_otp, send_otp_email
from models import User, sendOTPReq, VerifyOTPReq
from services.auth_service import get_current_active_user
from fastapi import Body
from services.otp_service import get_redis_connection
from dotenv import dotenv_values
from db_connection import get_db, get_connection
from services.email_service import send_reciept_email

config = dotenv_values(".env")
TTL_OTP_SECONDS = int(config.get("TTL_OTP_SECONDS", 160))

otp_router = APIRouter(prefix="/otp", tags=["OTP"])

@otp_router.get("/send-otp")
async def send_otp(requestOTP: sendOTPReq = Body(...), current_user: User = Depends(get_current_active_user)):
    otp = generate_otp()

    key = str(requestOTP.customer_id) + ":" + str(requestOTP.transaction_id)
    r = get_redis_connection()
    
    r.setex(key, TTL_OTP_SECONDS, otp)

    send_otp_email(current_user.email, otp)
    return {"message": "OTP sent"}

# @otp_router.post("/verify-otp")
# async def verify_otp(request: VerifyOTPReq, current_user: User = Depends(get_current_active_user), db=Depends(get_db)):
#     key = str(request.customer_id) + ":" + str(request.transaction_id)
#     r = get_redis_connection()
    
#     stored_otp = r.get(key)
#     if stored_otp is None:
#         return {"valid": False, "message": "OTP expired or not found"}

#     if stored_otp != request.otp:
#         return {"valid": False, "message": "Invalid OTP"}
    
#     try:
#         with db.cursor() as cursor:
#             cursor.execute('UPDATE `Transaction` SET Status = "OTP Verified" WHERE TransactionID=%s', (request.transaction_id,))
#             db.commit()
#     except Exception as e:
#         return {"valid": False, "message": "Database error: " + str(e)}



#     r.delete(key)


@otp_router.post("/verify-otp")
async def process_payment(request: VerifyOTPReq, current_user: User = Depends(get_current_active_user), db=Depends(get_db)):
    transaction_id = request.transaction_id
    customer_id = request.customer_id

    key = str(customer_id) + ":" + str(transaction_id)
    r = get_redis_connection()
    
    stored_otp = r.get(key)
    if stored_otp is None:
        return {"valid": False, "message": "OTP expired or not found"}

    if stored_otp != request.otp:
        return {"valid": False, "message": "Invalid OTP"}
    # get balance from customer account

    try:
        with db.cursor() as cursor:
            # Check Transaction exists
            cursor.execute("SELECT * FROM `Transaction` WHERE TransactionID=%s", (transaction_id,))
            transaction = cursor.fetchone()
            if not transaction:
                raise HTTPException(status_code=404, detail="Transaction not found")

            if transaction["CustomerID"] != customer_id:
                raise HTTPException(status_code=400, detail="Transaction does not belong to the customer")

            if transaction["PaidAt"] is not None:
                raise HTTPException(status_code=400, detail="Transaction is already paid")

            total_price = transaction["TotalPrice"]

            # Check Customer balance
            cursor.execute("SELECT Balance FROM Customer WHERE CustomerID=%s", (customer_id,))
            customer = cursor.fetchone()
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found")

            if customer["Balance"] < total_price:
                raise HTTPException(status_code=400, detail="Insufficient balance")

            # Deduct balance and mark transaction as paid
            new_balance = customer["Balance"] - total_price
            cursor.execute("UPDATE Customer SET Balance=%s WHERE CustomerID=%s", (new_balance, customer_id))
            cursor.execute('UPDATE `Transaction` SET PaidAt=NOW(), Status = "Paid" WHERE TransactionID=%s', (transaction_id,))
            send_reciept_email(transaction_id, current_user, db)
            db.commit()

            return {"message": "Payment processed successfully", "new_balance": new_balance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        r.delete(key)