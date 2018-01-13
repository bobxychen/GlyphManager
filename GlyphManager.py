import win32gui
import subprocess
import time
from PIL import ImageGrab
from PIL import Image
import string
import json

import os
import shlex
import struct
import platform
from ctypes import windll, create_string_buffer



def _get_terminal_size_windows():
    """Gets terminal width and length of a typical windows CMD terminal"""


    #from https://gist.github.com/jtriley/1108174, thank you very much for this hard to produce code!

    # stdin handle is -10
    # stdout handle is -11
    # stderr handle is -12
    h = windll.kernel32.GetStdHandle(-12)
    csbi = create_string_buffer(22)
    res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
    if res:
        (bufx, bufy, curx, cury, wattr,
         left, top, right, bottom,
         maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        sizex = right - left + 1
        sizey = bottom - top + 1
        return sizex, sizey


def BlockPrint(message, char_set, TermWidth=_get_terminal_size_windows()[0], WordWrap=True): #add option to alos auto create a cahracter if keyerror, generally Termwidth should be 80
    """Will correctly print and optionally wordwrap the output from createGlyphs"""

    final = {}

    TermWidth *= 0.96 # <- possibly the most fascinating and odd fix i've ever done. this will produce the correct output given the TermWidth. 4 is the min value to fix a line overflow issue, which I could not figure out the root cause of (but it did not affect the 1st and last lines of the result)
    # through an experiment with terminal at 200 wide, i found out there is a direct relationship between terminal size and this buffer needed. 100:4, 200:8 (any less and it will overlfow)


    char_width = len(char_set.values()[0].split("\n")[0])
    char_length = len(char_set.values()[0].split("\n"))

    if WordWrap:
        current_line_length = 0
        line = 1

        for each in message: 
            if current_line_length + char_width >= TermWidth:
                current_line_length = 0
                line += 1
                pass
            else:
                current_line_length += char_width

            each_map = char_set[each].split("\n")
            #print each + str(each_map)

            for e_i,i in enumerate(range((line-1) * char_length, line * char_length)):
                try:
                    final[i] += each_map[e_i]
                except KeyError:
                    final[i] = each_map[e_i]

    else:  #if this produces garbled output, you must resize terminal
        for each in message: 
            for i in range(char_length):
                try:
                    final[i] += char_set[each].split("\n")[i] 
                except KeyError:
                    final[i] = char_set[each].split("\n")[i]
    

    for each in final:
        print final[each]

def createGlyphs(input):
    """A complicated and hacky method to get a bitmap representation of the windows CMD font"""

    command_open = subprocess.Popen(["start", "cmd","/k", 'echo {}'.format(input)], shell = True)

    time.sleep(2) #time for window to appear

    #print win32gui.FindWindow(None, "C:\Windows\system32\cmd.exe")
    hwnd = win32gui.FindWindow(None, "C:\Windows\system32\cmd.exe")
    win32gui.SetForegroundWindow(hwnd)
    bbox = win32gui.GetWindowRect(hwnd)
    img = ImageGrab.grab(bbox)
    #img.show()

    length_of_chars = len(input) * 8  # +2 to compensate for the quotation marks
    combined_chars = img.crop((10,34,length_of_chars+9,45))
    #combined_chars.show()

    #nonetype error was caused by chaining the .show() wiutth the rest of the stuff

    chars = {x:"" for x in input}

    for i, each in enumerate(range(8,combined_chars.size[0]+9,8)):   #starts from 1, and +8 to compensate for the -8 below VVV
        #if i not in bad_indexes: #this is to avoid the first and last double quotation marks
        current_char = input[i]
        
        indiv_char = combined_chars.crop((each-8,0,each,11))
        
        w, h = indiv_char.size #should be 8 wide by 9 high

        for i2, pixel in enumerate(indiv_char.getdata()):  #tuple values can either be (0, 0, 0) or (192,192,192) for the default terminal colours
            if pixel == (192,192,192): 
                chars[current_char] += u"\u2588"

            else:
                chars[current_char] += " "

            if i2 % w == w-1: # we want it too look decent so overflow is neeeded onto the next lines
                # ^^^ before it was i2 % w == 0, but that lead to a trail behind character, so whats before 0? -1! so w-1!!!
                chars[current_char] += "\n"

        chars[current_char] = chars[current_char][:-1]  #this is to remove the last "\n"

    return chars


def saveChars(char_set, dest_file=os.path.join(os.path.dirname(__file__), "character_set.txt")):
    """Saves output from createGlyphs for future use"""

    with open(dest_file,"w+") as file:
        try:
            orig_chars = loadChars(dest_file)          #we must acutally load it before we save it, we simply save as a new dictionary, DO NOT APPEND
        except ValueError:
            #was empty file
            orig_chars = {}
        char_set.update(orig_chars)
        json.dump(char_set, file)

def loadChars(file=os.path.join(os.path.dirname(__file__), "character_set.txt")):
    """Loads existing glyphs to save time"""

    with open(file,"r") as f:
        return json.load(f)