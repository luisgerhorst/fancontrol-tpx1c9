#!/usr/bin/env python3

import time
import sys
from pathlib import Path
import logging

def main() -> int:
    logging.basicConfig(level=logging.DEBUG)

    temp_path=Path("/sys/class/hwmon/hwmon5/temp1_input")
    pwm_path=Path("/sys/class/hwmon/hwmon5/pwm1")
    pwm_enable_path=Path("/sys/class/hwmon/hwmon5/pwm1_enable")

    # sec_temp_path=Path("/sys/class/hwmon/hwmon5/temp1_input")

    interval=2
    # (enable_temp, pwm): increase to pwm if > enable_temp, decrease to pwm if < enable_temp
    tp_map = [(0, 0),
              (55, 0),
              (65, 40),   # 4500RPM
              (75, 80),   # 4800RPM
              (85, 120),
              (95, 255)]
    max_pwm_delta = 5 # only change by x pwm per interval

    last_temp = 0
    last_pwm = 0
    level_temp = 0

    while True:
        temp = int(temp_path.read_text()) / 1000

        pwm = None
        if temp >= level_temp:
            for (t,p) in tp_map:
                if temp >= t:
                    level_temp = t
                    pwm = p

        # Only reduce level if we are below the lower level's enable_temp.
        if temp < level_temp:
            for (t,p) in reversed(tp_map):
                if temp < t:
                    level_temp = t
                    pwm = p

        # Limit rate of pwm increase to prevent over-compensation.
        max_pwm = last_pwm + max_pwm_delta
        if pwm > max_pwm:
            pwm = max_pwm

        logging.info("%d %d" % (temp, pwm))
        pwm_path.write_text(str(pwm))
        pwm_enable_path.write_text("1")
        last_temp = temp
        last_pwm = pwm
        time.sleep(interval)
    return 0

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit
