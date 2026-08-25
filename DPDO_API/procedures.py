from django.db import connection

def get_category_winners(category_id: int):
    with connection.cursor() as cursor:
        cursor.execute("EXEC sp_GetCategoryWinners @CategoryId = %s", [category_id])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    for row in rows:
        row['is_podium'] = row['Position'] <= 3
    return rows


def get_registration_statistics():
    with connection.cursor() as cursor:
        cursor.execute("EXEC sp_GetRegistrationStatistics")

        registrations_by_advisor = cursor.fetchall()
        columns_1 = [col[0] for col in cursor.description]

        cursor.nextset()
        unauthorized_attempts = cursor.fetchone()[0]

        cursor.nextset()
        duplicate_attempts = cursor.fetchone()[0]

    return {
        'registrations_by_advisor': [
            dict(zip(columns_1, row)) for row in registrations_by_advisor
        ],
        'unauthorized_attempts': unauthorized_attempts,
        'duplicate_attempts': duplicate_attempts,
    }