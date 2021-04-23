Kodi Smart Home Service
=====================

This is a work to control and automate TV set, Soundbar, and smart
power plug from within CoreELEC/Kodi application.

It runs as a Kodi service monitoring all the connected devices within
from CoreELEC media center, turning on/off them according to Kodi status.

Right now, it's working for Sony Bravia TV, Samsung Soundbar, and Xiaomi
smart plugs.


Installation
============

Install the files into a folder called `service.kodismarthomeservice`
inside your Kodi installation's `addons` folder.

For the python dependencies, it's recommended to install entware/python
and its libraries.

Setup
=============
Go to
Kodi > Add-ons > My Add-ons > Services > Kodi Smart Home Service > Configure

And make sure that the TV's **IP address**, **MAC address**, **Input**
and **Brand** are selected.

**Do NOT change the PIN unless you've already configured the TV. When
you first enable the service you will set it.**

Enjoy!