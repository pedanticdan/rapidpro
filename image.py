#!/usr/bin/env python3

from PIL import Image  
from PIL import ImageDraw
from PIL import ImageFont

width = 150
height = 200

text = "ABS"

white = (255,255,255,255)
black = (0,0,0,255)

colors = [ "00AE42FF", "489FDFFF" ,"D32941FF", "FFFFFFFF" ]

def average(color):
    a = []
    for i in range(0,len(color),2):
        a.append(int(color[i:i+2],16))
    print(a)
    return sum(a[:3])/(len(a)-1)

def opposite(color):
    h = []
    for i in range(0,len(color),2):
        h.append(0xff - int(color[i:i+2],16))
    return h

img  = Image.new( mode = "RGBA", size = (width*4,height), color = black)
d = ImageDraw.Draw(img)

for i in range(len(colors)):
    h = opposite(colors[i])
    d.rounded_rectangle((i*width+1,0,width+i*width-1,height),12, (int(colors[i][0:2],16), int(colors[i][2:4],16),int(colors[i][4:6],16),int(colors[i][6:8],16)))
    fnt = ImageFont.truetype("/usr/share/fonts/truetype/msttcorefonts/Courier_New_Bold.ttf", 40)
    if average(colors[i]) > 127:
        fill=black
    else:
        fill=white
    d.text((width/5+width*i, height/3), text, font=fnt, fill=fill)
    print(i*width,0,width+i*width,height,":",colors[i],average(colors[i]))

img.save("tray2.png")
