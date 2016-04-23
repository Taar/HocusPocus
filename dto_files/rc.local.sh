######## AUTO export pins ##########
# NOTE: we believe it's a timming issue but exporting the pins causes issues
# with setting permissions on on the gpio devices
#echo bspm_P8_11_7 > /sys/devices/bone_capemgr.?/slots
#echo 45 > /sys/class/gpio/export

#echo bspm_P8_15_7 > /sys/devices/bone_capemgr.?/slots
#echo 47 > /sys/class/gpio/export

#echo bspm_P8_16_27 > /sys/devices/bone_capemgr.?/slots
#echo 46 > /sys/class/gpio/export

#echo bspm_P8_17_7 > /sys/devices/bone_capemgr.?/slots
#echo 27 > /sys/class/gpio/export

#echo bspm_P8_18_27 > /sys/devices/bone_capemgr.?/slots
#echo 65 > /sys/class/gpio/export

#echo bspm_P8_9_7 > /sys/devices/bone_capemgr.?/slots
#echo 70 > /sys/class/gpio/export

######## Set gpio device permissions ########

# Do not modify the order of thses commands

sleep 30

chown -R debian:gpio /sys/devices/platform/ocp/*.gpio/gpio
chown -R debian:gpio /sys/class/gpio
find /sys/devices/platform/ocp/*.gpio/gpio -type d -exec chmod 2775 {} \;
find /sys/devices/platform/ocp/*.gpio/gpio -name "direction" -exec chmod 0660 {} \;
find /sys/devices/platform/ocp/*.gpio/gpio -name "edge" -exec chmod 0660 {} \;
find /sys/devices/platform/ocp/*.gpio/gpio -name "value" -exec chmod 0660 {} \;

find /sys/devices/platform/ocp/*.gpio/gpio -name "active_low" -exec chmod 0660 {} \;
chmod 0220 /sys/class/gpio/export
chmod 0220 /sys/class/gpio/unexport
find /sys/devices/platform/ocp/*.gpio/gpio -name "uevent" -exec chmod 0660 {} \;
find /sys/devices/platform/ocp/*.gpio/gpio -name "autosuspend_delay_ms" -exec chmod 0660 {} \;
find /sys/devices/platform/ocp/*.gpio/gpio -name "control" -exec chmod 0660 {} \;
