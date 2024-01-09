# pymaster

Master server written in Python. Replacement for HLMaster

This project tested on latest [Xash3D FWGS](https://github.com/FWGS/xash3d-fwgs) engine.

If your client version does not return `IPv6` nodes, please checkout [this update](https://github.com/YGGverse/xash3d-fwgs/commit/afec7161842e928a5627d724e4fd7445fb7c3ee6).

## Features

* Added IPv6 support
* Includes latest Xash3D protocol updates (thanks to [@a1batross](https://github.com/a1batross))
* Clean `pymaster.py` codebase by [@xdettlaff](https://github.com/xdettlaff/pymaster)

## Install

* `git clone https://github.com/YGGverse/pymaster.git`
* `cd pymaster`
* `git checkout v2`
* `python3 pymaster.py -i :: -p 27010` for `IPv6` or `python3 pymaster.py -i 0.0.0.0 -p 27010` for `IPv4`
* `ufw allow 27010`

## Connect

### Yggdrasil

* `[201:5eb5:f061:678e:7565:6338:c02c:5251]:27010` | `hl.ygg:27010` | `hl.ygg.at:27010`