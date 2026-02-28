import time
import requests
import datetime
import meshtastic
import meshtastic.serial_interface
from pubsub import pub

API_URL = "http://localhost:8000/api/telemetry"

def on_receive(packet, interface):
    """Triggered every time the RAK module processes a packet."""
    try:
        decoded = packet.get('decoded', {})
        
        # Look specifically for Telemetry packets
        if decoded.get('portnum') == 'TELEMETRY_APP':
            telemetry = decoded.get('telemetry', {})
            
            # Check if this specific telemetry packet contains environment data
            if 'environmentMetrics' in telemetry:
                env_data = telemetry['environmentMetrics']
                
                # Extract the barometric pressure (usually in hPa/millibars)
                # We use .get(key, 0.0) as a fallback just in case the sensor glitches
                pressure = env_data.get('barometricPressure', 0.0)
                temperature = env_data.get('temperature', 0.0)
                
                telemetry_payload = {
                    "pressure": pressure,
                    "temperature": temperature,
                    "timestamp": datetime.datetime.now().isoformat()
                }

                # POST the data to your FastAPI backend
                response = requests.post(API_URL, json=telemetry_payload)
                print(f"Sent Environment Data: {response.status_code} - {telemetry_payload}")

    except Exception as e:
        print(f"Error parsing packet: {e}")

def main():
    print("Connecting to local RAK4630 via USB...")
    # Initialize the serial interface 
    interface = meshtastic.serial_interface.SerialInterface()
    
    # Subscribe to the 'receive' event (this catches local node broadcasts too)
    pub.subscribe(on_receive, "meshtastic.receive")
    
    print("Listening for environment telemetry... Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Closing connection...")
        interface.close()

if __name__ == "__main__":
    main()