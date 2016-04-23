#! /bin/bash

# Run as ROOT!

# Move dts files to correct locations
cp *.dts /lib/firmware/

# compile all the overlays
dtc -O dtb -o /lib/firmware/bspm_P8_11_7-00A0.dtbo -b 0 -@ /lib/firmware/bspm_P8_11_7-00A0.dts
dtc -O dtb -o /lib/firmware/bspm_P8_15_7-00A0.dtbo -b 0 -@ /lib/firmware/bspm_P8_15_7-00A0.dts
dtc -O dtb -o /lib/firmware/bspm_P8_16_27-00A0.dtbo -b 0 -@ /lib/firmware/bspm_P8_16_27-00A0.dts
dtc -O dtb -o /lib/firmware/bspm_P8_17_7-00A0.dtbo -b 0 -@ /lib/firmware/bspm_P8_17_7-00A0.dts
dtc -O dtb -o /lib/firmware/bspm_P8_18_27-00A0.dtbo -b 0 -@ /lib/firmware/bspm_P8_18_27-00A0.dts
dtc -O dtb -o /lib/firmware/bspm_P8_9_7-00A0.dtbo -b 0 -@ /lib/firmware/bspm_P8_9_7-00A0.dts
