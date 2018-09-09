#!/usr/bin/python
# -*- coding: utf-8 -*-
from gcode_manipulation import extract_number_for_var, extract_all_numbers, startwith
x,y = None,None
X0 = 0
Y0 = 0
z = 10


def sign(x):
    if(x<0):
        return -1
    elif(x>0):
        return 1
    else:
        return 0

def set_draw_orig(x0,y0):
    global X0, Y0
    X0 = x0
    Y0 = y0
    
def set_last_point(setx,sety,setz=10):
    global x, y
    x = setx
    y = sety
    z = setz
    
def draw_gcode(gcode, xorig = None, yorig = None):
    global x,y,z
    if(xorig!=None):
        global X0 #Change où on dessine
        X0 = xorig
    if(yorig!=None):
        global Y0
        Y0 = yorig
        
    for move in gcode:
        if(startwith(move,"G0") or startwith(move,"G1")):
            G, F, X, Y, Z = extract_all_numbers(move)
            X+=X0
            Y+=Y0
            if((x,y)!=(None,None)):
                if(z==Z):
                    if(z==10):
                        draw_line_air(x,y,X,Y)
                    elif(Z==0):
                        draw_line_pen(x,y,X,Y)
                    else:
                        draw_line_unknown(x,y,X,Y)
                else:
                    if(x==X and y==Y):
                        draw_point_z(x,y,Z)
                    else:
                        draw_line_error(x,y,X,Y)
            x,y,z=X,Y,Z

def draw_line_pen(x1,y1, x2,y2):
    c1 = pencolor1
    c2 = pencolor2
    draw_line_gradient(x1,y1,c1, x2,y2,c2, penalpha)
    
def draw_line_air(x1,y1, x2,y2):
    c1 = aircolor1
    c2 = aircolor2
    draw_line_gradient(x1,y1,c1, x2,y2,c2, airalpha)
    
def draw_line_unknown(x1,y1, x2,y2):
    c1 = (50,0,50)
    c2 = (255,0,255)
    draw_line_gradient(x1,y1,c1, x2,y2,c2, 128)
    
def draw_line_error(x1,y1, x2,y2):
    c1 = (0,50,0)
    c2 = (0,255,0)
    draw_line_gradient(x1,y1,c1, x2,y2,c2,180)
    
def draw_line_gradient(x1,y1,c1, x2,y2,c2, transparency = 255, style = "ellipse"):
    x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)
    c1 = color(*c1)
    c2 = color(*c2)  
    ellipseMode(RADIUS)
    noFill()
    stroke(c1,ellipsalpha)
    ellipse(x1,y1,2.5,2.5)
    stroke(c2,ellipsalpha)
    ellipse(x2,y2,2.5,2.5)
    if(style=="ellipse"):
        
        noStroke()
        radius = 1
        interval = radius
        distance = float((x2-x1)**2 + (y2-y1)**2)**0.5
        if(distance>0):
            s=-interval
            while(s<distance):
                s=min(s+interval,distance)
                #print "#",
                ratio = float(s)/distance
                fill(lerpColor(c1, c2, ratio),transparency)
                ellipse(x1+(x2-x1)*ratio,y1+(y2-y1)*ratio,radius,radius)
        #print ""
        
    elif(style=="point"):
        print(x1,y1, x2,y2)
        if(x1 != x2 or y1!=y2):
            if(abs(x1-x2)>abs(y1-y2)):
                i = 0
                while(x1+i!=x2):
                    i+=sign(x2-x1)
                    ratio = float(float(abs(i))/float(abs(x2-x1)))
                    stroke(lerpColor(c1, c2, ratio),transparency)
                    point(x1+i,y1+ratio*(y2-y1))
            else:
                i = 0
                while(y1+i!=y2):
                    i+=sign(y2-y1)
                    ratio = float(float(abs(i))/float(abs(y2-y1)))
                    stroke(lerpColor(c1, c2, ratio),transparency)
                    point(x1+ratio*(x2-x1),y1+i)
                    
def draw_point_z(x,y,zvalue):
    z0 = color(*pencolor2)
    z10 = color(*aircolor1)
    noFill()
    ratio = zvalue/10.0
    stroke(lerpColor(z0, z10, ratio),ellipsalpha)
    ellipseMode(RADIUS)
    
    ellipse(x,y,4,4)
    ellipse(x,y,3,3)
    
    

SOLID = 0
BLACKWHITE = 1
REDBLUE = 2
ORANGECYAN = 3

CURRENTCOLOR = None
        
def rotate_color_set():
    global CURRENTCOLOR
    CURRENTCOLOR = (CURRENTCOLOR+1)%4
    set_draw_color_set(CURRENTCOLOR)
        
def set_draw_color_set(selection):
    global pencolor1, pencolor2
    global aircolor1, aircolor2
    global penalpha, airalpha, ellipsalpha
    global CURRENTCOLOR 
    CURRENTCOLOR = selection

    if(selection==SOLID):
        pencolor1 = (0,0,0)
        pencolor2 = (0,0,0)
        aircolor1 = (192,192,192)
        aircolor2 = (192,192,192)
        penalpha = 255
        airalpha = 255
        ellipsalpha = 0
    elif(selection==BLACKWHITE):
        pencolor1 = (0,0,0)
        pencolor2 = (128,128,128)
        aircolor1 = (92,92,92)
        aircolor2 = (232,232,232)
        penalpha = 128
        airalpha = 64
        ellipsalpha = 128
    elif(selection==REDBLUE):
        pencolor1 = (64,0,0)
        pencolor2 = (255,0,0)
        aircolor1 = (0,0,128)
        aircolor2 = (128,255,255)
        penalpha = 128
        airalpha = 64
        ellipsalpha = 128
    elif(selection==ORANGECYAN):
        pencolor2 = (255,0,0)
        pencolor1 = (255,255,0)
        aircolor1 = (0,0,128)
        aircolor2 = (0,255,255)
        penalpha = 128
        airalpha = 64
        ellipsalpha = 128
        
set_draw_color_set(REDBLUE)
    
