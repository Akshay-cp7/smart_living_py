import cv2
import mediapipe as mp
import pyrebase
import socket
TCP_IP = '192.168.137.32'  # Replace with the IP address of your ESP8266
TCP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((TCP_IP, TCP_PORT))   

config = {
    "apiKey": "AIzaSyDM9P_mBPrsNchocc3ROzT17l2-rZhWH1Q",
    "authDomain": "smartliving-4b210.firebaseapp.com",
    "databaseURL": "https://smartliving-4b210-default-rtdb.firebaseio.com",
    "projectId": "smartliving-4b210",
    "storageBucket": "smartliving-4b210.appspot.com",
    "messagingSenderId": "166202571234",
    "appId": "1:166202571234:web:e1f69a97e5b37259e321bb",
    "measurementId": "G-MFCE6JT0J7"
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()
# Initialize MediaPipe Hand model
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

def stream_handler_d0(message):
    data = message["data"]
    if data == "ON":
        sock.send(b'A') 
    elif data == "OFF":
        sock.send(b'B')
        

def stream_handler_d1(message):
    data = message["data"]
    if data == "ON":
        sock.send(b'C')
    elif data == "OFF":
        sock.send(b'D')
       

def stream_handler_d2(message):
    data = message["data"]
    if data == "ON":
        sock.send(b'E')
        print('send D1ON')
    elif data == "OFF":
        sock.send(b'F')
        print('send D1OFF')

def stream_handler_d3(message):
    data = message["data"]
    if data == "ON":
        sock.send(b'G')
        print('send D2ON')
    elif data == "OFF":
        sock.send(b'H')
        print('send D2OFF')

my_stream_d0 = db.child("actions/D0").stream(stream_handler_d0)
my_stream_d1 = db.child("actions/D1").stream(stream_handler_d1)
my_stream_d2 = db.child("actions/D2").stream(stream_handler_d2)
my_stream_d3 = db.child("actions/D3").stream(stream_handler_d3)

# Initialize video capture
cap = cv2.VideoCapture(0)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Width
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

prev_state = None
# Initialize MediaPipe hands with max_num_hands set to 1
with mp_hands.Hands(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        max_num_hands=1) as hands:

    while cap.isOpened():  # continuous reading
        ret, frame = cap.read()
        if not ret:
            print("Ignoring empty camera frame.")
            continue

        # Convert the image to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        # Convert the image to grayscale
        #frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #results = hands.process(frame_gray)

        # Draw hand landmarks on the image
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get the coordinates of the thumb and index finger MCP (metacarpophalangeal) joint
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

                ring_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]
                pinky_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
                index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]   
                middle_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]

                # Get the y-coordinates of all finger tips
                thumb_tip_y = thumb_tip.y * frame.shape[0]
                index_tip_y = index_tip.y * frame.shape[0]
                index_mcp_y = index_mcp.y * frame.shape[0]
                middle_tip_y = middle_tip.y * frame.shape[0]
                middle_mcp_y = middle_mcp.y * frame.shape[0]
                ring_tip_y = ring_tip.y * frame.shape[0]
                ring_mcp_y = ring_mcp.y * frame.shape[0]
                pinky_tip_y = pinky_tip.y * frame.shape[0]
                pinky_mcp_y = pinky_mcp.y * frame.shape[0]

                # Get the handedness classification
                handedness = results.multi_handedness[0].classification[0].label

                # Check if it's the right hand
                if handedness == 'Left':
                    
                    if index_tip_y < index_mcp_y and middle_tip_y > middle_mcp_y and ring_tip_y > ring_mcp_y and pinky_tip_y > pinky_mcp_y:
                       current_state = 1

                    elif index_tip_y < index_mcp_y and middle_tip_y < middle_mcp_y and ring_tip_y > ring_mcp_y and pinky_tip_y > pinky_mcp_y:
                       current_state = 2
                    elif index_tip_y < index_mcp_y and middle_tip_y < middle_mcp_y and ring_tip_y < ring_mcp_y and pinky_tip_y > pinky_mcp_y:
                       current_state = 3
                    elif index_tip_y < index_mcp_y and middle_tip_y < middle_mcp_y and ring_tip_y < ring_mcp_y and pinky_tip_y < pinky_mcp_y:
                       current_state = 4
                        
                    else:
                        current_state = " "
                elif handedness == 'Right':
                    
                    if index_tip_y < index_mcp_y and middle_tip_y > middle_mcp_y and ring_tip_y > ring_mcp_y and pinky_tip_y > pinky_mcp_y:
                         current_state = 5
                    elif index_tip_y < index_mcp_y and middle_tip_y < middle_mcp_y and ring_tip_y > ring_mcp_y and pinky_tip_y > pinky_mcp_y:
                        current_state = 6
                    elif index_tip_y < index_mcp_y and middle_tip_y < middle_mcp_y and ring_tip_y < ring_mcp_y and pinky_tip_y > pinky_mcp_y:
                       current_state = 7
                    elif index_tip_y < index_mcp_y and middle_tip_y < middle_mcp_y and ring_tip_y < ring_mcp_y and pinky_tip_y < pinky_mcp_y:
                        current_state = 8
                    else:
                        current_state = " "

                if current_state != prev_state:

                    if current_state == 1:
                        db.child("actions/D0").set("ON")
                    elif current_state == 5:
                        db.child("actions/D0").set("OFF")
                    elif current_state == 2:
                        db.child("actions/D1").set("ON")
                    elif current_state == 6:
                        db.child("actions/D1").set("OFF")
                    if current_state == 3:
                        db.child("actions/D2").set("ON")
                    elif current_state == 7:
                        db.child("actions/D2").set("OFF")
                    elif current_state == 4:
                        db.child("actions/D3").set("ON")
                    elif current_state == 8:
                        db.child("actions/D3").set("OFF")
                        
                    
                    
                    prev_state = current_state



  

        cv2.imshow('MediaPipe Hands', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release resources
cap.release()
sock.close()
cv2.destroyAllWindows()
my_stream_d0.close()
my_stream_d1.close()
my_stream_d2.close()
my_stream_d3.close()
