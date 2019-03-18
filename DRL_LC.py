#hello world
#!/usr/bin/python
import pygame, sys
import pygame.locals as GAME_GLOBALS
import pygame.event as GAME_EVENTS
import time
import math
import os
import json
import requests

pygame.init() #initalize pygame
pygame.font.init() #initialize pygame font

dimensions = pygame.display.Info() #this grabs the screen's size in pixels

dim_w = dimensions.current_w/15 #the screens width in pixels
dim_h = dimensions.current_h/8 #the screens height in pixels. 

#surface = pygame.display.set_mode((dimensions.current_w, dimensions.current_h), pygame.FULLSCREEN)#creates the main window
surface = pygame.display.set_mode((dim_w, dim_h))
pygame.display.set_caption('DRL')

windo_size = pygame.Surface.get_size(surface) #get the size of the tiny window. 

pygame.mouse.set_visible(0)#remvoes the mouse icon rom the main screen
surface.fill((0,0,0)) #color the screen black

#define your meet credentials here. 
meet_id = 'md199gasarz2' #usapl meet

#USAPL Platform IDs
platform_id = 'pugzn7prxroz' #Platform
#define meet password
password = 'squat900'

#define local server IP. 
meet_url = "192.168.86.124"

#these are the URLs used to make requests to liftingcast
light_url = "http://"+meet_url+"/api/meets/"+meet_id+"/platforms/"+platform_id+"/lights"
set_clock_url = "http://"+meet_url+"/api/meets/"+meet_id+"/platforms/"+platform_id+"/clock"
start_clock_url= "http://"+meet_url+"/api/meets/"+meet_id+"/platforms/"+platform_id+"/start_clock"
reset_clock_url= "http://"+meet_url+"/api/meets/"+meet_id+"/platforms/"+platform_id+"/reset_clock"
password_data={"password":password}

    
def liftingcast_post(url,data):
	
	try:
		r = requests.post(url,json=data)
		place_image("network_good.png",2,windo_size[0]/8,windo_size[1]/8)
		pygame.display.update()
		time.sleep(1)
	except:
		print ("error sending referee light data, check internet connection")
		network_error = True
		place_image("network_bad.png",2,windo_size[0]/8,windo_size[1]/8)
		pygame.display.update()
		time.sleep(1)

def draw_circle(location): #debug circles to tell if the remotes are funcitoning. 
	global surface, windo_size
	if location == "left":
		pygame.draw.circle(surface, (0, 148, 71), [32 , 120],5, 0)
		
	elif location == "chief":
		pygame.draw.circle(surface, (0, 148, 71), [62 , 120],5, 0)
		
	else:
		pygame.draw.circle(surface, (0, 148, 71), [92 , 120],5, 0)



class timer():
	global password_data, start_clock_url, reset_clock_url
	def __init__(self):
		self.started = False
		
	def toggle(self):
		#start the clock
		if self.started == True:
				
			try:
				#the clock is already started, pause it.
				r = requests.post(reset_clock_url,json=password_data)
				self.started = False #reset. 
				place_image("network_good.png",2,windo_size[0]/8,windo_size[1]/8)
				pygame.display.update()
				time.sleep(1)
			
			except: 
				place_image("network_bad.png",2,windo_size[0]/8,windo_size[1]/8)
				pygame.display.update()
				time.sleep(1)
		else:
                r = requests.post(start_clock_url,json=password_data)
			#the clock is paused, start it.
			try:
				r = requests.post(start_clock_url,json=password_data)
				self.started = True
				place_image("network_good.png",2,windo_size[0]/8,windo_size[1]/8)
				pygame.display.update()
				time.sleep(1)
			except:
				place_image("network_bad.png",2,windo_size[0]/8,windo_size[1]/8)
				pygame.display.update()
				time.sleep(1)
			



def place_image(logo,scaling_factor, x,y):
	global surface
	#this will be a function which takes in an image, scaling size, and location and prints it on the screen. 
	raw_logo = pygame.image.load(logo) #load in the image you want displayed
	image_dimensions = raw_logo.get_rect().size
	x_scale = (((float(dimensions.current_h/100)*scaling_factor))*float(image_dimensions[0]))/(float(image_dimensions[1]))
	scaled_logo_main = pygame.transform.scale(raw_logo, ((int(x_scale)),(dimensions.current_h/100)*scaling_factor))
	logo_position = scaled_logo_main.get_rect()
	logo_position.centerx = x #this should be the middle of the screen
	logo_position.centery = y
	surface.blit(scaled_logo_main, logo_position)
	
	
	
	
class referee:
	def __init__(self):
		self.red = False
		self.blue = False
		self.yellow = False
		self.white = False
		
	def reset(self):
		self.red = False
		self.blue = False
		self.yellow = False
		self.white = False


def check_state():
	global left, chief, right, Timer, left_light, chief_light, right_light
	
	#color the indicator dots. 
	if (left.red or left.blue or left.yellow or left.white):
		draw_circle("left")
		
	if (chief.red or chief.blue or chief.yellow or chief.white):
		draw_circle("chief")
		
	if (right.red or right.blue or right.yellow or right.white):
		draw_circle("right")
		
	pygame.display.update()

	if (left.red or left.blue or left.yellow or left.white):
		#print ("left side: ",left.red, left.blue, left.yellow, left.white)
		if (chief.red or chief.blue or chief.yellow or chief.white):
			#print ("chief side; ", chief.red, chief.blue, chief.yellow, chief.white)
			if (right.red or right.blue or right.yellow or right.white):
				draw_circle(right)
				#print ("right side:", right.red, right.blue, right.yellow, right.white)
				drl_decisions_to_liftingcast_decisions(left.white, left.red, left.blue,left.yellow,chief.white,chief.red,chief.blue,chief.yellow,right.white,right.red, right.blue,right.yellow)
				print("decision detected, attempting to post to liftingcast")
				left.reset()
				chief.reset()
				right.reset()
				Timer.started = False


def drl_lights_to_liftingcast_decision(white, red, blue, yellow):
    if white:
        return "good"
    else:
        return "bad"

def drl_lights_to_cards(red, blue, yellow):
    return {"red": red, "blue": blue, "yellow": yellow}

def drl_lights_to_decision_cards(white, red, blue, yellow):
    """Takes 4 booleans representing a referee's white light and red, blue, and
    yellow cards and returns a map of decision and cards.
    white, red, blue, yellow
    => {"decision": "good" | "bad",
        "cards": {"red": True | False,
                  "blue": True | False,
                  "yellow": True | False}}
    """
    return {"decision": drl_lights_to_liftingcast_decision(white, red, blue, yellow),
            "cards": drl_lights_to_cards(red, blue, yellow)}

def drl_decisions_to_liftingcast_decisions(left_white,
                                           left_red,
                                           left_blue,
                                           left_yellow,
                                           head_white,
                                           head_red,           
                                           head_blue,
                                           head_yellow,
                                           right_white,
                                           right_red,
                                           right_blue,
                                           right_yellow):
    global password, light_url
    
    liftingCastLights =  {
        "left": drl_lights_to_decision_cards(left_white,
                                             left_red,
                                             left_blue,
                                             left_yellow),
        "head": drl_lights_to_decision_cards(head_white,
                                             head_red,
                                             head_blue,
                                             head_yellow),
        "right": drl_lights_to_decision_cards(right_white,
                                              right_red,
                                              right_blue,
                                              right_yellow),
        "select_next_attempt":True,
        "select_next_attempt_delay":1,
        "clear_lights_delay":3,
        "password":password
    }
    #q.put(liftingCastLights)
    #now we have our json package ready to send, call the proper function to send it. 
    liftingcast_post(light_url, liftingCastLights)


def liftingcast_decisions_to_result(liftingcast_decision_cards_dict):
    """Takes a map of referee to decision and cards and returns a result for the
    lift.
    {"head": {"decision": <decision>, "cards": <cards>},
     "left": {"decision": <decision>, "cards": <cards>},
     "right": {"decision": <decision>, "cards": <cards>}}
    => "good" | "bad"
    """
    num_good_decisions = len([dc["decision"] for dc in liftingcast_decision_cards_dict.values() if dc["decision"] == "good"])

    if num_good_decisions < 2:
        return "bad"
    else:
        return "good"

def are_valid_light_and_cards(white, red, blue, yellow):
    return (not (white and (red or blue or yellow)) and
            (white or red or blue or yellow))

def empty_decisions():
    return {
        "left": {
            "decision": None,
            "cards": {
                "red": None,
                "blue": None,
                "yellow": None
            }
        },
        "head": {
            "decision": None,
            "cards": {
                "red": None,
                "blue": None,
                "yellow": None
            }
        },
        "right": {
            "decision": None,
            "cards": {
                "red": None,
                "blue": None,
                "yellow": None
            }
        }
    }





#initialize 3 instances of the referee class. 
left = referee()
chief = referee()
right = referee()
#Initialize timer.
Timer = timer()

#main loop. 
while True:
	surface.fill((0,0,0)) #color the screen black
	place_image("drl_logo.png", 10,windo_size[0]/2, windo_size[1]/2)
	place_image("network_normal.png",2,windo_size[0]/8,windo_size[1]/8)
	for event in GAME_EVENTS.get():
		if event.type == pygame.KEYDOWN:

			#Left referee
			if event.key == pygame.K_a: #left red card
				left.red = True
				left.white = False
				#print("left red")
				
			if event.key == pygame.K_s: #left blue card
				left.blue = True
				left.white = False
				#print("left blue")
				
			if event.key == pygame.K_d: #left yellow card
				left.yellow = True
				chief.white = False
				#print("left yellow")
				
			if event.key == pygame.K_w: #left white
				left.white = True
				left.red = False
				left.blue = False
				left.yellow = False
				#print("left white")
				
			#chief referee
			if event.key == pygame.K_j: #chief red card
				chief.red = True
				chief.white = False
				#print("chief red")
				
			if event.key == pygame.K_k: #chief blue card
				chief.blue = True
				chief.white = False
				#print("chief blue")
				
			if event.key == pygame.K_l: #chief yellow card
				chief.yellow = True
				chief.white = False
				#print("chief yellow")
				
			if event.key == pygame.K_i: #chief white
				chief.white = True
				chief.red = False
				chief.blue = False
				chief.yellow = False
				#print("chief white")
				
			if event.key == pygame.K_c: #control the clock
				#start/reset the clock function
				#print("clock button pressed")
				Timer.toggle()
				
			#right referee
			if event.key == pygame.K_f: #right red card
				right.red = True
				right.white = False
				print("right red")
				
			if event.key == pygame.K_g: #right blue card
				right.blue = True
				right.white = False
				print("right blue")
				
			if event.key == pygame.K_h: #right yellow card
				right.yellow = True
				right.white = False
				
				print("right yellow")
			if event.key == pygame.K_t: #right white
				right.white = True
				right.red = False
				right.blue = False
				right.yellow = False
				print("right white")
				
			if event.key == pygame.K_ESCAPE:
				pygame.quit()
				sys.exit()
					
	#check for 
	check_state()
	pygame.display.update()
