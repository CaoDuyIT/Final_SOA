from fastapi import Depends, HTTPException
from db_connection import get_db

async def update_booking_total_price(transaction_id: int, db=Depends(get_db)):
    with db.cursor() as cursor:
        # Check if roomType exists
        cursor.execute("SELECT * FROM `Transaction` WHERE TransactionID=%s", (transaction_id,))

        # Calculate total price
        cursor.execute("""
            SELECT SUM(rt.Price) AS TotalPrice
            FROM TransactionRoom tr
            JOIN Room r ON tr.RoomID = r.RoomID
            JOIN RoomType rt ON r.RoomTypeID = rt.RoomTypeID
            WHERE tr.TransactionID = %s
        """, (transaction_id))
        total_price = cursor.fetchone()["TotalPrice"]

        # Update total price in Transaction
        cursor.execute("""
            UPDATE `Transaction`
            SET TotalPrice = %s
            WHERE TransactionID = %s
        """, (total_price, transaction_id))