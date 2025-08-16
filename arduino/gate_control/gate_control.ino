#include <Servo.h>

// Define pins for ultrasonic sensor
const int trigPin = 9;
const int echoPin = 10;

// Define pins for servo motors
const int entryServoPin = 11;
const int exitServoPin = 6;

// Define servo objects
Servo entryGateServo;
Servo exitGateServo;

// Define gate open and close positions
const int gateOpenAngle = 90; // Angle when gate is open
const int gateCloseAngle = 0; // Angle when gate is closed

// Define detection range (in cm)
const int detectionRange = 4;

// Timing variables
unsigned long objectDisappearTime = 0; // Time when the object is no longer detected
const unsigned long closeDelay = 4000; // Close gate 4 seconds after object disappears
bool isExitGateOpen = false;

// Entry gate state variables
bool isEntryGateOpen = false;
bool entryGateMoving = false;          // Indicates if the entry gate is currently moving
int entryTargetAngle = gateCloseAngle; // Target angle for the entry gate

// Exit gate state variables
bool exitGateMoving = false;          // Indicates if the exit gate is currently moving
int exitTargetAngle = gateCloseAngle; // Target angle for the exit gate

// Ultrasonic sensor debounce variables
const unsigned long debounceTime = 500; // Time to wait for consistent detection
unsigned long lastDetectionTime = 0;
bool objectDetected = false;

void setup()
{
  Serial.begin(9600); // Initialize serial communication

  // Setup ultrasonic sensor pins
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // Attach servos
  entryGateServo.attach(entryServoPin);
  exitGateServo.attach(exitServoPin);

  // Initialize gates to closed position
  entryGateServo.write(gateCloseAngle);
  exitGateServo.write(gateCloseAngle);
  delay(500); // Allow time for the servos to reach the closed position

  Serial.println("Gate Control System Ready");
}

void loop()
{
  // Check for serial commands (entry gate)
  if (Serial.available() > 0)
  {
    char command = Serial.read();

    if (command == 'O' && !entryGateMoving)
    { // Open entry gate
      entryTargetAngle = gateOpenAngle;
      isEntryGateOpen = true;
      Serial.println("Opening Entry Gate...");
    }
    else if (command == 'C' && !entryGateMoving)
    { // Close entry gate
      entryTargetAngle = gateCloseAngle;
      isEntryGateOpen = false;
      Serial.println("Closing Entry Gate...");
    }
  }

  // Smoothly move the entry gate towards the target angle
  if (!entryGateMoving)
  {
    moveGateSmoothly(entryGateServo, entryTargetAngle, entryGateMoving);
  }

  // Control exit gate based on ultrasonic sensor
  int distance = getFilteredDistance(); // Get stable distance measurement

  Serial.print("Distance: ");
  Serial.println(distance);

  // Check if an object is detected within range
  if (distance <= detectionRange)
  {
    if (!objectDetected)
    {
      objectDetected = true;
      lastDetectionTime = millis(); // Record the time of detection
    }
    else if (millis() - lastDetectionTime >= debounceTime && !isExitGateOpen && !exitGateMoving)
    {
      // Object consistently detected, open the gate
      exitTargetAngle = gateOpenAngle;
      isExitGateOpen = true;
      Serial.println("Opening Exit Gate...");
    }
    objectDisappearTime = millis(); // Reset the disappear timer as long as the object is detected
  }
  else
  {
    if (objectDetected)
    {
      objectDetected = false;         // Object no longer detected
      objectDisappearTime = millis(); // Record the time when the object disappeared
    }
  }

  // Close the gate 4 seconds after the object disappears
  if (isExitGateOpen && !objectDetected && millis() - objectDisappearTime >= closeDelay && !exitGateMoving)
  {
    exitTargetAngle = gateCloseAngle;
    isExitGateOpen = false;
    Serial.println("Closing Exit Gate...");
  }

  // Smoothly move the exit gate towards the target angle
  if (!exitGateMoving)
  {
    moveGateSmoothly(exitGateServo, exitTargetAngle, exitGateMoving);
  }

  delay(10); // Small delay to stabilize loop
}

// Function to smoothly move a gate
void moveGateSmoothly(Servo &gateServo, int targetAngle, bool &gateMoving)
{
  int currentAngle = gateServo.read();

  if (currentAngle != targetAngle)
  {
    gateMoving = true; // Mark the gate as moving

    // Calculate the direction of movement
    int direction = (targetAngle > currentAngle) ? 1 : -1;

    // Move the servo in small steps
    for (int angle = currentAngle; angle != targetAngle; angle += direction)
    {
      // Ensure we don't overshoot the target angle
      if ((direction == 1 && angle > targetAngle) || (direction == -1 && angle < targetAngle))
      {
        angle = targetAngle;
      }

      // Write the new angle to the servo
      gateServo.write(angle);

      // Dynamic delay for smoother motion (ease-in, ease-out)
      int distanceToTarget = abs(targetAngle - angle);
      int delayTime = map(distanceToTarget, 0, abs(targetAngle - currentAngle), 10, 50);
      delay(delayTime);
    }

    // Ensure the servo reaches the exact target angle
    gateServo.write(targetAngle);
    delay(10);

    gateMoving = false; // Mark the gate as stopped

    // Print the current state of the gate
    if (targetAngle == gateOpenAngle)
    {
      Serial.println("Gate Opened");
    }
    else
    {
      Serial.println("Gate Closed");
    }
  }
}

// Function to measure distance with ultrasonic sensor (using a moving average)
int getFilteredDistance()
{
  const int numReadings = 5; // Number of samples for smoothing
  int total = 0;

  for (int i = 0; i < numReadings; i++)
  {
    total += measureDistance();
    delay(10); // Short delay between readings
  }

  return total / numReadings; // Return the average distance
}

// Function to measure distance using ultrasonic sensor
int measureDistance()
{
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  return duration * 0.034 / 2; // Convert time to distance (cm)
}