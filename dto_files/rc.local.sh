######## AUTO export pins ##########
# Do not modify the order of thses commands

echo bspm_P8_11_7 > /sys/devices/bone_capemgr.?/slots
echo 45 > /sys/class/gpio/export

echo bspm_P8_15_7 > /sys/devices/bone_capemgr.?/slots
echo 47 > /sys/class/gpio/export

echo bspm_P8_16_27 > /sys/devices/bone_capemgr.?/slots
echo 46 > /sys/class/gpio/export

echo bspm_P8_17_7 > /sys/devices/bone_capemgr.?/slots
echo 27 > /sys/class/gpio/export

echo bspm_P8_18_27 > /sys/devices/bone_capemgr.?/slots
echo 65 > /sys/class/gpio/export

echo bspm_P8_9_7 > /sys/devices/bone_capemgr.?/slots
echo 70 > /sys/class/gpio/export

######## Set gpio device permissions ########

sleep 30

chown -R debian:gpio /sys/class/gpio
chmod 0220 /sys/class/gpio/export
chmod 0220 /sys/class/gpio/unexport
