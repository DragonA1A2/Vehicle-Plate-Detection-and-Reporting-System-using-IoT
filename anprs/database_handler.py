import pymysql
from datetime import datetime
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


class DatabaseHandler:
    def __init__(self):
        self.connection_params = {
            "host": os.getenv("DB_HOST", "localhost"),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", ""),  # XAMPP default has no password
            "database": os.getenv("DB_NAME", "vehicle_management"),  # Use Django's DB
            "port": int(os.getenv("DB_PORT", 3306)),
        }

        # Setup logging
        logging.basicConfig(
            filename="access_log.txt",
            level=logging.INFO,
            format="%(asctime)s - %(message)s",
        )

    def connect(self):
        return pymysql.connect(**self.connection_params)

    def check_plate_authorized(self, plate_number):
        try:
            with self.connect() as connection:
                with connection.cursor() as cursor:
                    sql = """
                    SELECT * FROM vms_vehicle
                    WHERE license_plate = %s AND status = 'approved'
                    """
                    cursor.execute(sql, (plate_number,))
                    result = cursor.fetchone()
                    return bool(result)
        except Exception as e:
            logging.error(f"Database error: {str(e)}")
            return False

    def log_access_attempt(self, plate_number, authorized):
        status = "AUTHORIZED" if authorized else "UNAUTHORIZED"
        logging.info(f"Access attempt - Plate: {plate_number} - Status: {status}")
