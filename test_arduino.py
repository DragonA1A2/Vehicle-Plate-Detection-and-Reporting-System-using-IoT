from anpr.gate_controller import GateController
import time

def test_arduino():
    print("Testing Arduino connection...")
    
    # Create controller
    controller = GateController()
    
    # Try to connect
    if controller.connect():
        print("Testing gate operation...")
        
        # Test opening gate
        if controller.open_gate():
            print("Gate command sent successfully!")
        else:
            print("Failed to send gate command!")
            
        # Wait a bit
        time.sleep(6)
        
    # Clean up
    controller.close()

if __name__ == "__main__":
    test_arduino() 