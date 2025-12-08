async def get_rooms_available(room_type_id: int, checkin: str, checkout: str, db):
    with db.cursor() as cursor:

        status_available = 1

        query = """
            Select room.RoomID, room.RoomNumber, room.RoomTypeID, room.StatusID
            From Room room
            Where room.RoomTypeID = %s
            And room.StatusID = %s
            And room.RoomID not in (
                Select t.RoomID
                From `Transaction` t
                Where t.Status in ('Pending', 'Paid', 'CheckedIn')
                And (
                    %s < t.CheckOut
                    And %s > t.CheckIN
                )
            )
        """

        cursor.execute(query, (room_type_id, status_available, checkin, checkout))

        return cursor.fetchall()

async def get_rooms_by_type(room_type_id: int, db):
     with db.cursor() as cursor:
            query = """
                Select RoomID, RoomNumber, RoomTypeID, StatusID
                From Room
                Where RoomTypeID = %s
            """
            cursor.execute(query, (room_type_id,))

            return cursor.fetchall()

async def get_rooms_available_by_type(room_type_id: int, db):
     with db.cursor() as cursor:

        status_available = 1

        query = """
            Select room.RoomID, room.RoomNumber, room.RoomTypeID, room.StatusID
            From Room room
            Where room.RoomTypeID = %s
            And room.StatusID = %s
        """

        cursor.execute(query, (room_type_id, status_available))

        return cursor.fetchall()
     
async def get_all_room_types(db):
     with db.cursor() as cursor:

        query = """
            SELECT * FROM RoomType
        """

        cursor.execute(query)

        return cursor.fetchall()