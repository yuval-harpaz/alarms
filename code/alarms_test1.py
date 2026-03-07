import socketio
import time

# Create a Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print('Connected to test server')

@sio.event
def connect_error(data):
    print(f"The connection failed! {data}")

@sio.event
def disconnect():
    print('Disconnected from server')

# The node example shows socket.on('alert', ...)
# In python-socketio, we can decorate functions with @sio.on
# Note: The namespace is '/test'
@sio.on('alert', namespace='/test')
def on_alert(alerts):
    for alert in alerts:
        print('Test alert:', alert)
        # This will trigger every 5 seconds with demo data

if __name__ == '__main__':
    try:
        # Connect to test server - no API key required!
        # The URL in the example is 'https://redalert.orielhaim.com/test'
        # In python-socketio, the namespace is passed separately or as part of the URL
        # We use the base URL and specify the namespace to stay consistent with the library docs.
        sio.connect('https://redalert.orielhaim.com', namespaces=['/test'])
        
        print("Listening for alerts... (Ctrl+C to stop)")
        # Keep the script running to receive events
        sio.wait()
    except KeyboardInterrupt:
        print("\nStopping...")
        sio.disconnect()
    except Exception as e:
        print(f"Error: {e}")
