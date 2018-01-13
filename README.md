# GlyphManager
Python module that can dynamically create big terminal font (ie not hardcoded)


### About

This is a package that allows you to create, print (display), save and load "glyphs" or in other words, bitmap fonts of the windows terminal.
It is intended to be flexible and dynamic to be able to map out any font in your terminal and most importantly, to save you from hardcoding font for a project ever again (tedious and hard to maintain)!


### Output

It will produce a python dictioary with the larger bitmap rendition of each character so you can print it out with the associated function
It can also be saved to harddisk in json format by calling saveChars().

### Example

Here are some examples of the output from it
![Example](image_alphabet.PNG)
![Example](image_text.PNG)
![Example](image_time.PNG)
### Requirements

-Python 2
-Windows (will not work in other OS)

### Credits

Thank you very much to jtriley for providing the module to find the windows terminal width!!
https://gist.github.com/jtriley/1108174
