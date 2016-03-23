'''
Created on Feb 26, 2016

@author: Christopher Elliott
'''
import random
import numpy
import pygame
from numpy.ma.core import floor_divide
from operator import attrgetter
import sys


if __name__ == '__main__':
    pass


MAX_SEATS = 159         #maximum seats in the aircraft
MAX_FIRST_CLASS = 12    #maximum first class seats
MAX_TIME = 62           #maximum time a passenger can arrive at (days)
MAX_PARTY = 5           #maximum party size

#seat class holds variables to determine seat occupancy and seat types
class seat:
    id = -1             #seat number
    passClass = -1       #seating class (0 for economy, 1 for first) 
    taken = False       #seat is empty if False
    window = False      #window seat
    isle = False        #isle seat
    coords = (-1,-1)    #seat coordinates
    weight = 0          #compatibility weighting

#passenger class holds variables to determine passenger seating priorities
class passenger:
    id = -1                 #passengers id
    seat = -1               #assigned seat number, range of 1 to MAX_SEATS
    window = False          #prefers window seat
    isle = False            #prefers isle seat
    passClass = 0           #passengers seating class (0 for economy, 1 for first)               
    arrivalTime = -1        #time passenger checked in, range of 1 to MAX_TIME

#creates a given amount of passengers with pseudo-random characteristics
#outputs a List of passengers
def generatePassengers(num):
    if num > MAX_SEATS:     #ensures a List of passengers does not exceed given MAX_SEATS
        return 0
    
    randPassengers = []   #List for storage of generated passengers
    firstClass = 0
    for i in range(0,num):
        tempPassenger = passenger()     #creates new passenger object
        tempPassenger.id = i            #passenger gets id of iterator
        if firstClass < MAX_FIRST_CLASS:        #if first class seats are still available
            random.seed(None)   #seeds the pseudo-random generator with the current system time
            classList = [0,1]
            tempPassenger.passClass = numpy.random.choice(classList)      #pseudo-randomly gives the passenger a class
            if tempPassenger.passClass == 1:
                firstClass = firstClass + 1     #if passenger assigned first class, increment first class seats taken
        prefChoices = [1,2,3]   #preference choices
        random.seed(None)
        choice = numpy.random.choice(prefChoices)   #pseudo random preference choice
        if choice == 1:     #window preference
            tempPassenger.window = True
            tempPassenger.isle = False
        elif choice == 2:     #isle preference
            tempPassenger.window = False
            tempPassenger.isle = True
        elif choice == 3:     #no preference
            tempPassenger.window = False
            tempPassenger.isle = False
        random.seed(None)   
        tempPassenger.arrivalTime = numpy.random.randint(1,MAX_TIME)    #gets a pseudo random integer for the arrival time
        randPassengers.append(tempPassenger)        #appends new passenger to list
    randPassengers.sort(key = lambda x: x.arrivalTime, reverse = False)     #sort passengers based on arrival time
    return randPassengers

#creates a seating configuration based on a Boeing 737-800
#returns a list of configured seats
def configureSeats():
    seatList = []       #list of configured seats
    for i in range(0,MAX_FIRST_CLASS):  #configuring first class seats
        tempSeat = seat()       #new seat object
        tempSeat.id = i  
        tempSeat.passClass = 1      #seat is first class
        if i % 4 == 0 or i % 4 == 3:     #seat is on either far side of the plane it is a window seat
            tempSeat.window = True
            tempSeat.isle = False
        if i % 4 == 1 or i % 4 == 2:     #seat is on the inside of the row then it is an isle seat
            tempSeat.window = False
            tempSeat.isle = True
        #configuring graphics
        x = ((i%3)*10) + 1   #10 pixels between start of each seat plus pad of 1 px to center
        ypad = 0 
        if i % 4 == 3 or i % 4 == 0:    #seat on bottom side of aisle
            ypad = 34
        else:
            ypad = 11
        y = ypad + (i%2)*10   #seats are 10 pixels apart plus different padding for each side of the aisle 2 is the number of seats per row (bottom and top)
        tempSeat.coords = (x,y)
        
        seatList.append(tempSeat)       #adds new seat to list
        
    for i in range(MAX_FIRST_CLASS,MAX_SEATS):      #economy seats
        tempSeat = seat()       #new seat object
        tempSeat.id = i 
        tempSeat.passClass = 0      #seat is economy
        if i % 6 == 0 or i % 6 == 5:     #seat is on either far side of the plane it is a window seat
            tempSeat.window = True
            tempSeat.isle = False
        if i % 6 == 2 or i % 6 == 3:     #seat is on the inside of the row then it is an isle seat
            tempSeat.window = False
            tempSeat.isle = True
        if i % 6 == 1 or i % 6 == 4:       #middle seat
            tempSeat.window = False
            tempSeat.isle = False
        #configuring graphics
        x = 32 + floor_divide(i-MAX_FIRST_CLASS,6)*10   #for each row, increment x by 10 achieved through deviding (i subtracting the first class seats) by number of seats per row and taking the floor of the result
        ypad = 0
        if i % 6 == 3 or i % 6 == 4 or i % 6 == 5:    #seat on bottom of aisle
            ypad = 34
        else:
            ypad = 1
        y = ypad + (i%3)*10         #three seats per row (bottom and top)
        tempSeat.coords = (x,y)
        
        seatList.append(tempSeat)       #adds new seat to list
    return seatList             
          

#assigns passengers a seat based on their preferences and available seats
#outputs a list of seats
def assignSeats(passList, seatList):
    if len(passList) > len(seatList):       #check that passengers don't exceed seat count
        return 0
    for i in range (0,len(passList)):       #iterates through passenger list
        for j in range(0,len(seatList)):    #iterates through seat list
            seatList[j].weight = 0
            if passList[i].window == True and seatList[j].window == True:       #passenger window preference met
                seatList[j].weight = seatList[j].weight + 10
            if passList[i].isle == True and seatList[j].isle == True:       #passenger isle preference met
                seatList[j].weight = seatList[j].weight + 10
            #checking seats around selected seat
            if j < MAX_FIRST_CLASS:     #seat in first class
                if j % 4 == 0 or j % 4 == 2:      #first or third seat in row
                    if seatList[j+1].taken == False:    #next seat in row is free
                        seatList[j].weight = seatList[j].weight + 2
                    else:
                        seatList[j].weight = seatList[j].weight - 2
                elif j % 4 == 1 or j % 4 == 3:  #second or fourth seat in row
                    if seatList[j-1].taken == False:    #previous seat in row is free
                        seatList[j].weight = seatList[j].weight + 2
                    else:
                        seatList[j].weight = seatList[j].weight - 2
                if j + 4 < MAX_FIRST_CLASS: 
                    if seatList[j+4].taken == False:    #seat behind is empty
                        seatList[j].weight = seatList[j].weight + 1
                if j - 4 > 0:
                    if seatList[j-4].taken == False:    #seat in front empty
                        seatList[j].weight = seatList[j].weight + 1
            else:       #economy seats
                if j % 6 == 0 or j % 6 == 3:    #first or fourth seat in row
                    if seatList[j+1].taken == False:    #next seat in row is free
                        seatList[j].weight = seatList[j].weight + 2
                    else:
                        seatList[j].weight = seatList[j].weight - 2
                elif j % 6 == 1 or j % 6 == 4:   #second or fifth seat in row
                    if seatList[j+1].taken == False:    #next seat in row
                        seatList[j].weight = seatList[j].weight + 1
                    else:
                        seatList[j].weight = seatList[j].weight - 1
                    if seatList[j-1].taken == False:    #previous seat in row
                        seatList[j].weight = seatList[j].weight + 1
                    else:
                        seatList[j].weight = seatList[j].weight - 1
                elif j % 6 == 2 or j % 6 == 5:    #third or sixth seat in row
                    if seatList[j-1].taken == False:    #previous seat in row is free
                        seatList[j].weight = seatList[j].weight + 2
                    else:
                        seatList[j].weight = seatList[j].weight - 2  
                if j + 6 < MAX_SEATS: 
                    if seatList[j+6].taken == False:    #seat behind is empty
                        seatList[j].weight = seatList[j].weight + 1
                if j - 6 > MAX_FIRST_CLASS:
                    if seatList[j-6].taken == False:    #seat in front empty
                        seatList[j].weight = seatList[j].weight + 1 
        sameClass = [x for x in seatList if x.passClass == passList[i].passClass and x.taken == False]          #filter the list getting all seats of correct class
        maxSeat = max(sameClass, key=attrgetter("weight"))      #maximum weighted seat
        passList[i].seat = maxSeat.id       #assigning seat
        seatList[maxSeat.id].taken = True       #marking seat as taken

    return passList

  
                    
#main function for display
def main(num):
    #initializing seats and passengers
    seats = configureSeats() 
    tpassengers = generatePassengers(num)
    passengers = assignSeats(tpassengers, seats)    
    
    pygame.display.init()         
    planeDisplay = pygame.display.set_mode((279,63))   #setting display region
    pygame.display.set_caption("Seating")       #Title for display
    plane = pygame.image.load("C:/users/chris/desktop/plane.png")    #load plane seating image
    firstTaken = pygame.image.load("C:/users/chris/desktop/firstClassTaken.png").convert_alpha()    #load first class taken image
    economyTaken = pygame.image.load("C:/users/chris/desktop/economyClassTaken.png").convert_alpha()    #load economy class taken image
    planeDisplay.blit(plane,(0,0))
    pygame.display.flip()
    displayExit = False
    imageList = []
    for i in range(0,len(passengers)):  #iterate through seats
        if passengers[i].passClass == 1:
            imageList.append(firstTaken.copy())
            planeDisplay.blit(imageList[i],seats[passengers[i].seat].coords)    #display first class passenger
        else:
            imageList.append(economyTaken.copy())
            planeDisplay.blit(imageList[i],seats[passengers[i].seat].coords)    #display economy passenger
    pygame.display.flip()
    while not displayExit:      #display loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   #if user exits program
                displayExit = True
                pygame.quit()
                sys.exit()
        
main(100)   #assign seats   