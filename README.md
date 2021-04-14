Project documentation : 

What you will need :
Raspberry pi 3+/4 , 32 Gb Sd card , balena Etcher software for uploading image to Sd card , SD formatter to format Sd card, and user account of balenaOs where you can get balena Os image. And power source adapter with Usb cable.
Resources : https://dashboard.balena-cloud.com/apps, https://www.balena.io/etcher/?

 Building balena Os for respected Board (I am using raspberry pi 3b+ with 64bit OS ):
Balena supports 67 devices and we can use any language from Node.js, Python, Golang. ZFirst you need to download balena os from cloud https://dashboard.balena-cloud.com/apps, according to user selections user downloaded Os image accordingly,  when you downloaded balenaOS from the dashboard, extract this image to Sd card using balena etcher https://www.balena.io/etcher/?Before doing this you need to format Sd card with Sd formatter. After uploading the image to Sd card you should have a file called resin-wifi in the folder /system-connections/ in Sd card.
[connection]
id=balena-wifi
type=wifi

[wifi]
hidden=true
mode=infrastructure
ssid=My Awesome WiFi Ssid

[ipv4]
method=auto

[ipv6]
addr-gen-mode=stable-privacy
method=auto

[wifi-security]
auth-alg=open
key-mgmt=wpa-psk
psk=super_secret_wifi_password

From resin-wifi file users can change ssid and psk as i wrote in bold above.After that simply put the sd card in RPI and power up the pi in a few minutes dashboard is up with rpi connection and shows default files on it.  

2-Architecture: designing Architecture diagram here: https://app.diagrams.net/#G1sCN8RgmM226EpccBgSQzRW5ANWBQZE8n
3- Adding balena variables :
4 - GCP configuration : 
5- Dynmexil SDk: 
   a- E-Manual Link (AX-12A): https://emanual.robotis.com/docs/en/dxl/ax/ax-12a/
   b- Protocol: https://emanual.robotis.com/docs/en/dxl/protocol1/ 
                User can find here the  ROBOTIS’s DYNAMIXEL Protocol Compatibility Table with reference and structure with detail explanation of packets 
   c- Github Repo: https://github.com/ROBOTIS-GIT/DynamixelSDK 
   d- Control table: There are two types of control table 
          a- EEPROM (https://emanual.robotis.com/docs/en/dxl/ax/ax-12a/#control-table-of-eeprom-area), 
	  b- RAM (https://emanual.robotis.com/docs/en/dxl/ax/ax-12a/#control-table-of-ram-area)
	Data in the RAM Area is reset to initial values when the power is reset(Volatile). On the other hand, data in the EEPROM Area is maintained even when the device is powered off(Non-Volatile). In both tables R and R/RW shows the tag of readable and rewritable address before chossing any motor first check these tags from both tables


