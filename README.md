# HocusPocus

## Configuration

Supports Debian with kernel 4.1+

Example config file (`prod.ini`):

```
[paths]
pid_file = /tmp/door_controller.pid
error_file = /tmp/door_controller_error.txt

[fabric]
local_python_path = /home/taar/.virtualenvs/HocusPocus/bin/python
# Don't forget to update this on each new release ;P
project_version = 0.1
host_env_path = /home/debian/.Envs/door_controller
```

Example supervisord program file:

```
[program:HocusPocus]
command=/home/debian/.Envs/door_controller/bin/python /home/debian/.Envs/door_controller/lib/python3.4/site-packages/HocusPocus-0.1-py3.4.egg/hocuspocus/run.py /home/debia/hocuspocus.ini
process_name=%(program_name)s
numprocs=1
priority=999
autostart=true
autorestart=unexpected
startsecs=10
startretries=3
stopwaitsecs=10
user=debian
redirect_stderr=false
stdout_logfile=/home/debian/logs/door_controller/stdout.log
stdout_logfile_maxbytes=1MB
stdout_logfile_backups=10
stdout_capture_maxbytes=1MB
stdout_events_enabled=false
stderr_logfile=/home/debian/logs/door_controller/stderr.log
stderr_logfile_maxbytes=1MB
stderr_logfile_backups=10
stderr_capture_maxbytes=1MB
stderr_events_enabled=false
```

## Running it

`python hocuspocus/run.py development.ini`

## Fabfile

Note: you'll need a different environment with fabric installed.

`fab -H <host> deploy:development.ini`

## Beaglebone Black GPIO permissions:

Below describes how to give the debian user access to the gpio devices. 

In `/etc/udev/rules.d/` create the file `80-gpio.rules`
```
# Install in: /etc/udev/rules.d/
KERNEL=="gpio*", SUBSYSTEM=="gpio", ACTION=="add", PROGRAM="/bin/fix_udev_gpio.sh"
```
Recommended you place this file in /bin

```
#!/bin/bash
#
# This file will change the user, group and permissions in both the
# /sys/devices/virtual/gpio and /sys/class/gpio path directories.
#
# DO NOT change the order of the commands below, they are optimized so that
# commonly created files and directories are changed first.
#

chown -R debian:gpio /sys/devices/virtual/gpio
chown -R debian:gpio /sys/class/gpio
find /sys/devices/virtual/gpio -type d -exec chmod 2775 {} \;
find /sys/devices/virtual/gpio -name "direction" -exec chmod 0660 {} \;
find /sys/devices/virtual/gpio -name "edge" -exec chmod 0660 {} \;
find /sys/devices/virtual/gpio -name "value" -exec chmod 0660 {} \;

find /sys/devices/virtual/gpio -name "active_low" -exec chmod 0660 {} \;
chmod 0220 /sys/class/gpio/export
chmod 0220 /sys/class/gpio/unexport
find /sys/devices/virtual/gpio -name "uevent" -exec chmod 0660 {} \;
find /sys/devices/virtual/gpio -name "autosuspend_delay_ms" -exec chmod 0660 {} \;
find /sys/devices/virtual/gpio -name "control" -exec chmod 0660 {} \;
```

Make sure to change the user in the above script if it differs and add debian to the gpio group.

Note: Make sure `80-gpio.rules` (rw-r--r--) and `fix_udev_gpio.sh` (rwxr-x---) have the correct file permissions.

If the above doesn't work, you can try to modify the permissions for the devices instead of the
file links stored in `/sys/devices/virtual/`

```
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
```

## Relay States
HIGH Relay OFF
LOW Relay ON

## Script logic
1. Check to see if the pid exists
    - if it does, exit
2. Check relay state
    - Should be HIGH
3. Unlock the door
4. Check replay state
    - Should be LOW
5. Hold door open for X seconds
6. Lock the door
7. Check replay state
    - Should be HIGH
8. Exit

## Failure
On fail the script should log the issue and exit.
 - Try to recover to a locked state.
 - Log the issue
 - Flesh Leds dislaying the error code

## Error Code
- edit the pid file with the error numbers on the first line and the error
  message on the second
- flash the red led to the number error code

The Red Led on error will flash to display the error codes:
- Each flash consists of being held high for 500ms and low for 500ms
- Hold led high for 1 second (Start of the error code)
- Hold Low for 1 second
- the second part is the replay that failed the check
    - 1 flash being the first
    - 2 flashes being the second
    - 3 flashes being both
- Hold Low for 1 second
- first part is where in the script it failed
    - 1 flash being the first check
    - 2 flashes being the second check
    - 3 flashes being the third check
- Hold Low for 1 second
