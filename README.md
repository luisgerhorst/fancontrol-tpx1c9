# fancontrol-tpx1c9

Linux fancontrol script for Lenovo ThinkPad X1 Carbon Gen 9 (20XXS0Y800).

## Install

``` sh
sudo -s
cd /usr/local/stow
git clone git@github.com:luisgerhorst/fancontrol-tpx1c9.git 
stow --target=/ \
  --ignore=.git --ignore=.gitignore --ignore=LICENSE --ignore=README.md \
  fancontrol-tpx1c9
systemctl daemon-reload
systemctl start fancontrol-tpx1c9
systemctl enable fancontrol-tpx1c9

# Inspect the log
sudo journalctl -f -u fancontrol-tpx1c9
```
