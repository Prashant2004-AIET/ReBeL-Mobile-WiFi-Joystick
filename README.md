\# ReBeL Mobile WiFi Joystick



Control an igus ReBeL 6-axis robot arm's joints from a phone browser over WiFi, using igus's official CRI interface (via cri\_lib) and a small Python/Flask bridge server.



Phone (any browser, same WiFi) -> touch joystick (index.html) -> WebSocket -> Python bridge server (server.py) -> CRI protocol (cri\_lib) -> iRC software -> ReBeL robot



No native mobile app is needed -- the phone just opens a webpage served by the Python script.



\## Safety First



This controls a real, physical robot arm. Before using this project:



\- Always keep the robot's e-stop within reach while testing.

\- Test in iRC's simulation mode first before connecting to the real robot.

\- Start with a low speed cap and increase it only once you've verified joint directions behave as expected.

\- Test one axis at a time before attempting anything more complex.

\- This project includes a software watchdog that auto-stops the robot if the phone stops sending input. Do not remove this safety check.

\- This project is provided as-is with no warranty. You are responsible for safe operation of your own hardware.



\## Requirements



\- An igus ReBeL (or other CPR/igus robot) with iRC installed and running

\- A PC/laptop with an Ethernet connection to the robot controller and a WiFi connection your phone can also join

\- Python 3.9+

\- cri\_lib: https://github.com/CommonplaceRobotics/CRI-Python-Lib



\## Project Structure



robot\_joystick/

&#x20; server.py            (Python bridge: WebSocket to CRI)

&#x20; templates/index.html (Mobile joystick web page)

&#x20; README.md



The templates folder must be named exactly that -- Flask looks for HTML pages there automatically.



\## Installation



pip install flask flask-socketio eventlet

pip install git+https://github.com/CommonplaceRobotics/CRI-Python-Lib



\## Configuration



Edit the top of server.py:

ROBOT\_IP = "192.168.3.11"

ROBOT\_PORT = 3920

MAX\_VELOCITY\_PERCENT = 15

WATCHDOG\_TIMEOUT = 0.4



Test in simulation first: set ROBOT\_IP to 127.0.0.1 and ROBOT\_PORT to 3921 while iRC is running in simulation mode. Only switch to the real robot's IP and port 3920 once behavior is confirmed correct.



\## Running



python server.py



Expected output shows a successful connection message and the address to open on your phone. On your phone (same WiFi network as the PC), open that address in a browser. Select a joint (J1-J6), then drag the on-screen joystick up/down to jog that joint. Release to stop, or tap the red STOP button at any time.



\## How It Works



\- server.py connects to the robot via cri\_lib's CRIController, which speaks igus's CRI protocol over TCP. It exposes a small web server (Flask) and a WebSocket (Flask-SocketIO) so the phone can send live jog commands without page reloads.

\- set\_jog\_values sets the speed (as a percentage of max) for all six arm joints simultaneously; only the selected joint gets a nonzero value per phone input.

\- A watchdog thread monitors how long it's been since the last message from the phone. If that exceeds WATCHDOG\_TIMEOUT, it force-stops all jog motion, protecting against dropped WiFi connections or a closed browser tab.

\- templates/index.html is a single-page joystick UI using WebSockets to stream jog values to the server roughly every 150ms while held.



\## Troubleshooting



CRIConnectionError on connect but ping succeeds: cri\_lib's internal connect timeout may be too short for your network.

OSError about socket address already in use: port already in use, find the process with netstat and stop it, or change the port.

Phone shows Internal Server Error: templates/index.html missing or templates folder misnamed.

Phone can't reach the page at all: phone and PC not on the same WiFi/subnet, or a firewall is blocking the connection.



\## License



Add your preferred license here (e.g. MIT) before publishing.

