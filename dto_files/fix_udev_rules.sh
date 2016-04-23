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
