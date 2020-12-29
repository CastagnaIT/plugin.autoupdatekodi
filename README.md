# AutoUpdateKodi Plugin for Kodi (plugin.autoupdatekodi)

[![Kodi version](https://img.shields.io/badge/kodi%20versions-19-blue)](https://kodi.tv/)
[![GitHub release](https://img.shields.io/github/release/castagnait/plugin.autoupdatekodi.svg)](https://github.com/castagnait/plugin.autoupdatekodi/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Contributors](https://img.shields.io/github/contributors/castagnait/plugin.autoupdatekodi.svg)](https://github.com/castagnait/plugin.autoupdatekodi/graphs/contributors)

## Disclaimer

This add-on is provided "as is" without warranty of any kind, either express or implied. Use at your own risk.

## Main features

- Allows you to browse the Kodi downloads for Windows from the mirror address
- Allows to upgrade/downgrade Kodi in a fully automatic way (no UAC confermation, no Setup guide, auto reboot Kodi)
- Allows you to get any info of the GitHub PR's referred to each Setup of the nightly builds
- Allows you to keep stored the previous installed Setups for a fast rollback

## Installation & Updates

This add-on is compatible only with Kodi 19.x and higher<br/>
for Windows operative systems only (no Windows Store/UWP)

- Open Kodi and in the Add-ons browser, choose Install from zip file
- Navigate in to the Home/downloads folder then install the repository file `repository.castagnait-1.0.x.zip`
- Return to the add-ons browser and choose Install from repository then select CastagnaIT repository and install the add-on

**DOWNLOAD FROM REPOSITORY NOT READY YET**<br/>
[CastagnaIT Repository for KODI 19.x MATRIX - repository.castagnait-1.0.0.zip](https://github.com/castagnait/repository.castagnait/raw/matrix/repository.castagnait-1.0.0.zip)

## How to upgrade/downgrade Kodi in a fully automatic way

**Prerequisites: You must have the user account as administrator of your computer (usually you already are)**

This feature allow you to install each Kodi setup that you choose in fully automatic way, that means:
- Allows you to avoid UAC prompt confirmation
- No Setup installation guide
- Kodi will be restarted automatically when the installation will be completed

So you no longer need the mouse or other manual interaction to make a Kodi update/downgrade

**How to enable it:**
1) Open the add-on setting
2) Enable `Automatic installations`
3) Select `Install Task`

When you choose to uninstall this add-on remember to execute `Delete Task` from the settings,
nothing happens if you do not do this, but an unused entry called `Kodi_Install_NoUAC` remains saved in the Windows Task Scheduler.

## License

Licensed under The MIT License.
