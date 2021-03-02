# Hue Sync
## Sync your media with your Hue lights WITHOUT a Hue Sync Box!

# [Download](https://github.com/TimTrayler/hue-sync/releases/download/v2.2/hue-sync-v2.2.zip)
## [v2.2](https://github.com/TimTrayler/hue-sync/releases/tag/v2.2)

# How does it work?
Hue Sync takes a screenshot of your desktop every few seconds, gets the main color and changes the color of your lights!

# WIP
- Better tkinter-menu
- Search Light and Group IDs

# How to setup (simple)
1. Press the Link button on your Hue Bridge
2. Run the script in the next 30s
3. Open ```src/config.json``` and add the lamps and groups to the ```lamps``` and ```groups``` lists.
4. Done!

# How to setup (advanced)?
1. [Follow these instructions](https://developers.meethue.com/develop/get-started-2/)
2. Open ```src/config.json```
3. Set ```adress``` to the IP Adress of your Hue Bridge __or__ auto
4. Set ```bridge_number``` to the bridge you want to use (```0``` is the first bridge you connected to your wifi if you have multiple; only required if you have more than one bridge in your wifi and use ```adress: auto```)
5. Set ```user``` to your credentials __or__ to ```create``` (when using ```create``` you need to press the link button 30s before starting the script for the first time)
6. Add the lamp ids to ```lamps```
7. Change the additional settings like ```updatespermilliseconds``` to improve performance, make it smoother or something.
8. Install the dependencies, start the script, watch your movie and enjoy!

# Dependencies
- opencv-python
- pyautogui
- requests
- tkinter
- pygubu
- rgbxy
- numpy
- winshell (only if on windows)
