This program only works on pitft displays.
This program also needs python's tkinter module to run, to install it, do "python3 -m pip install pygame".
Once you have both of these things, run the program called "clock.py" in sudo mode. It must be run with root permissions or else it will not work, since it needs to overwrite certain drivers. If you dont have root access, well ... sorry.
To modify the clock's settings, edit the file called "manifest.json" in the folder called "utils".

The top line text on the clock is the time.
The bottom line of text on the clock is the brightness percentage.
The up and down arrows in the top left corner control the brightness of the screen.