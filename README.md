# pymaster

Master server written in Python. Replacement for HLMaster

## Features

* Added IPv6 support
* Includes latest Xash3D protocol updates
* Clean `pymaster.py` codebase by [@xdettlaff](https://github.com/xdettlaff/pymaster)

## Install

* `git clone https://github.com/YGGverse/pymaster.git`
* `cd pymaster`
* `git checkout v2`
* `ufw allow 27010`
* `python3 pymaster.py -i :: -p 27010` for `IPv6` or `python3 pymaster.py -i 0.0.0.0 -p 27010` for `IPv4`