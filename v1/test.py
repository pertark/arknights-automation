from adb_shell.adb_device import AdbDeviceTcp, AdbDeviceUsb
from adb_shell.auth.sign_pythonrsa import PythonRSASigner

# Load the public and private keys
adbkey = r"C:\Users\patri\.android\adbkey"
with open(adbkey) as f:
    priv = f.read()
with open(adbkey + '.pub') as f:
    pub = f.read()
signer = PythonRSASigner(pub, priv)

# Connect
device1 = AdbDeviceTcp('localhost', 5555, default_transport_timeout_s=9.)
device1.connect(rsa_keys=[signer], auth_timeout_s=0.1)

# Send a shell command
ak = 'com.YoStarEN.Arknights'
response1 = device1.shell('am start -n com.YoStarEN.Arknights')
startup = device1.shell('monkey -p com.YoStarEN.Arknights 1')
