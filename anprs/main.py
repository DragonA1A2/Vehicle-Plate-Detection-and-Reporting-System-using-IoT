from plate_processor import PlateProcessor
from database_handler import DatabaseHandler
from gate_controller import GateController
import cv2
import time
import logging


def main():
    # Initialize components
    plate_processor = PlateProcessor()
    db_handler = DatabaseHandler()
    gate_controller = GateController()

    # Connect to Arduino
    if not gate_controller.connect():
        print("Failed to connect to Arduino. Exiting...")
        return

    try:
        while True:
            try:
                # Check for Arduino feedback (exit gate sensor)
                feedback = gate_controller.read_serial_feedback()
                if feedback:
                    if "Vehicle detected at exit" in feedback:
                        print("Processing exit gate operation...")
                        continue

                # Process entrance gate
                print("Waiting for vehicle at entrance...")
                frame = plate_processor.capture_image()
                if frame is None:
                    continue

                # Detect and process plate
                plate_img = plate_processor.detect_plate(frame)
                if plate_img is None:
                    print("No plate detected")
                    continue

                # Extract plate number
                plate_number = plate_processor.extract_text(plate_img)
                if not plate_number:
                    print("Could not read plate number")
                    continue

                print(f"Detected plate number: {plate_number}")

                # Check if plate is authorized
                is_authorized = db_handler.check_plate_authorized(plate_number)

                # Log the attempt
                db_handler.log_access_attempt(plate_number, is_authorized)

                if is_authorized:
                    print("Access granted - Opening entrance gate")
                    gate_controller.operate_gate_with_timer(5)
                else:
                    print("Access denied - Unauthorized vehicle")

                time.sleep(0.1)  # Small delay to prevent CPU overuse
            except Exception as e:
                print(f"Error in main loop: {e}")
                # Optionally log to a file
                with open("anpr_system.log", "a") as logf:
                    import traceback

                    logf.write(traceback.format_exc() + "\n")
                continue
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        gate_controller.close_gate()
        gate_controller.close()


if __name__ == "__main__":
    main()
