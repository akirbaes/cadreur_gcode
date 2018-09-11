from gcode_manipulation import *
from gcode_draw import draw_gcode, set_draw_orig, set_last_point
from gcode_draw import set_draw_color_set, SOLID, BLACKWHITE, REDBLUE, ORANGECYAN
import os
filename = "jab4c20case_1.gcode"

border = 8
set_draw_color_set(REDBLUE)
#print("Arguments:",this.args)
try:
    filename=os.environ['USEFILE']
except:
    print("No USEFILE parameter given: using default filename")
    
#Initialiser le Gcode
#On peut le manipuler
gcode = import_gcode(filename)
print("Opened "+filename)
gcode = scale(gcode,1,1)
#gcode = rotate(gcode,1.756)
#gcode = shift(gcode,50,50)
#gcode = fit_inside(gcode,480,480,keep_ratio=True)

#Initialiser les variables de l'affichage de l'écran
minx,maxx,miny,maxy = get_borders(gcode)
print("X: %f to %f"%(minx,maxx))
print("Y: %f to %f"%(miny,maxy))

screenwidth = int(ceil(max(maxx, maxx-minx)))
screenheight = int(ceil(max(maxy, maxy-miny)))
print("Width: %d  Height: %d"%(screenwidth,screenheight))


def setup():
    size(screenwidth+border*2,screenheight+border*2)
    
def draw_background():
    #Dessine les boites de la fenêtre
    noStroke()
    fill(0)
    rect(0,0,2048,2048)
    fill(232)
    rect(0, 0, screenwidth+border*2, screenheight+border*2)
    fill(255)
    rect(border, border, screenwidth, screenheight)
    #Dessine le cadre des positions dessinées
    noFill()
    stroke(248)
    cadrex=max(0,minx)
    cadrey=max(0,miny)
    rect(cadrex+border, cadrey+border, max(maxx,maxx-minx)-cadrex, max(maxy,maxy-miny)-cadrey)
    #Croix de l'origine
    stroke(160)
    origx = border+max(0,-minx)
    origy = border+max(0,-miny)
    line(origx-8,origy,origx+8,origy)
    line(origx,origy-8,origx,origy+8)

def draw():
    global gcode

    draw_background()
    set_draw_orig(border+max(0,-minx),border+max(0,-miny))

    ####Prends une capture d'écran de la zone de dessin
    set_last_point(None,None)
    draw_gcode(gcode)
    partialSave = get(0,0,screenwidth+border*2,screenheight+border*2)
    partialSave.save(filename+".png")
    print("Saved image "+filename+".png")
    noLoop()
    exit()
