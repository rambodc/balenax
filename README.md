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


2- basic Architecture:

3- Explanation: 

4- requirements: 

5- Further tests: 


