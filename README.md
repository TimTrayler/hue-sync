# Hue Sync
## Sync your media with your Hue lights WITHOUT a Hue Sync Box!

# How does it work?
Hue Sync takes a screenshot of your desktop every few seconds, gets the main color and changes the color of your lights!

# WIP
- Support for rooms or groups

#How to setup?
1. [Follow these instructions](https://developers.meethue.com/develop/get-started-2/)
2. Open ```src/config.json```
3. Set ```adress``` to the IP Adress of your Hue Bridge
4. Set ```user``` to your credentials
5. Add the lamp ids to ```lamps```
6. Change the additional settings like ```updatespermilliseconds``` to improve performance, make it smoother or something.
7. Start the script, watch your movie and enjoy!
