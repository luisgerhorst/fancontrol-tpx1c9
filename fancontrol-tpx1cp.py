#!/usr/bin/env python3

import time
import sys
from pathlib import Path
import logging

CPU_PATH = list(Path('/').glob('sys/devices/platform/thinkpad_hwmon/hwmon/hwmon*/temp1_input'))[0]

# (enable_temp, pwm): increase to pwm if > enable_temp, decrease to pwm if < enable_temp
CPU_MAP = [(0, 0),
           (55, 0),
           (75, 40),   # 4800RPM
           (85, 80),   # 4800RPM
           (90, 160),
           (95, 255)]

CPU_TEMP_HIST_MAX = 30
CPU_TEMP_HIST = list()

def get_cpu_pwm(cpu_level):
    global CPU_PATH
    global CPU_MAP
    global CPU_TEMP_HIST_MAX
    global CPU_TEMP_HIST

    curr_temp = int(CPU_PATH.read_text()) / 1000
    CPU_TEMP_HIST.append(curr_temp)
    if len(CPU_TEMP_HIST) > CPU_TEMP_HIST_MAX:
        CPU_TEMP_HIST.pop(0)
    temp = sum(CPU_TEMP_HIST)/len(CPU_TEMP_HIST)

    if temp >= CPU_MAP[cpu_level][0]:
        for (l,(t,p)) in enumerate(CPU_MAP):
            if temp >= t:
                cpu_level = l

    # Only reduce level if we are below the lower level's enable_temp.
    if temp < CPU_MAP[cpu_level][0]:
        for (l,(t,p)) in reversed(list(enumerate(CPU_MAP))):
            if temp < t:
                cpu_level = l

    return cpu_level, curr_temp, CPU_MAP[cpu_level][1]


# /sys/devices/pci0000:00/0000:00:06.0/0000:04:00.0/nvme/nvme0/hwmon3/temp1_crit
NVME_PATH = list(Path('/').glob('sys/devices/pci0000:00/0000:00:06.0/0000:04:00.0/nvme/nvme0/hwmon*/'))[0]
NVME_MAX = int(NVME_PATH.joinpath("temp1_max").read_text()) / 1000
NVME_CRIT = int(NVME_PATH.joinpath("temp1_crit").read_text()) / 1000

def get_nvme_pwm():
    global NVME_PATH
    global NVME_MAX

    temp = int(NVME_PATH.joinpath("temp1_input").read_text()) / 1000

    pwm = 0
    crit = False
    if temp >= NVME_MAX-10:
        pwm = 40
    if temp >= NVME_MAX:
        pwm = 255
    if temp >= NVME_CRIT-5:
        pwm = 255
        crit = True

    return temp, pwm, crit

def main() -> int:
    logging.basicConfig(level=logging.DEBUG)

    INTERVAL=2
    MAX_PWM_DELTA = 40
    PWM_PATH = list(Path('/').glob('sys/devices/platform/thinkpad_hwmon/hwmon/hwmon*/pwm1'))[0]
    PWM_ENABLE_PATH = list(Path('/').glob('sys/devices/platform/thinkpad_hwmon/hwmon/hwmon*/pwm1_enable'))[0]

    cpu_level = 0
    last_pwm = 0

    while True:
        cpu_level, cpu_temp, cpu_pwm = get_cpu_pwm(cpu_level)
        nvme_temp, nvme_pwm, nvme_crit = get_nvme_pwm()

        pwm = max(cpu_pwm, nvme_pwm)

        # Limit rate of pwm increase to prevent over-compensation.
        max_pwm = last_pwm + MAX_PWM_DELTA
        if pwm > max_pwm and not nvme_crit:
            pwm = max_pwm

        logging.info("cpu %d %d, nvme %d %d => %d" % (cpu_temp, cpu_pwm, nvme_temp, nvme_pwm, pwm))
        PWM_PATH.write_text(str(pwm))
        PWM_ENABLE_PATH.write_text("1")
        last_pwm = pwm

        time.sleep(INTERVAL)
    return 0

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit
