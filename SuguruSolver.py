'''
Suguru Solver

Version 1 - Initial Version
Version 2 - Add puzzle name
Version 3 - Create and use puzzle save/load directory under current working directory 
Version 4 - Improve the draw6x6grid() function to be more efficient in drawing the grid and 
            reduce size of grid entry fields to make drawing border bigger
Version 5 - Major change to enable 5x5,6x6,7x7 and 8x8 Suguru puzzles to be handled
Version 6 - Change to use Tkinter SaveAs and File Open filedialog classes rather than self build dialog windows to Save and Load puzzles
            Also change file type from '.txt' to '.sugN' where N is the grid size (5,6,7,8)
Version 7 - Remove 'Check Numbers' and 'Check Outline' buttons and replace by a single 'Check' button that calls the Check() function to do both checks
            Also modify the Check to check the outline for single unconnected vertical or horizontal lines which should not be in an outline.
Version 8 - Remove exec() statements for creating Entry and replace with list variables  
Version 9 - Remove mutable global data types (lists) and immutable global datatypes that are not changed from global keyword statements
Version 10- Save and Load puzzle array as json formatted data file
Version 11- Bug fix -When using 'askyesno' messagebox set default to 'no' to force choice of yes.
Version 12- Change location of saved Suguru puzzles from current working directory to Appdata\SuguruSolver folder
'''

from tkinter import *    # this does not load all of tkinter - it does not load the ttk modules or messagebox for instance
from tkinter import ttk  # this is needed for the combobox - it is in the ttk part of tkinter 
from tkinter import messagebox
from tkinter import filedialog
from pathlib import Path
import math
import os
import json
from PIL import Image, ImageGrab,ImageWin
import win32print
import win32ui

# Private modules
import Sugurusolve as sol

#Global mutable data types
Entry_Names=[]
Puzzle_Array=[]
Copy_Puzzle_Array=[]
#Global immutable data types
SquareHeightWidth=0
GridSize=0
SquareSide=0
filetype=''
puzzle_path=''
drawing_enabled=False
puzzle_checked =False
delete_line=False

# Start of function definitions

# Function to Draw the Grid and the data entry fields according to the size of the puzzle
def DrawGrid():
    global SquareSide,SquareHeightWidth
# If there is an existing grid the delete all the lines and entry fields before drawing new grid
    if OldGridSize!=0:
        puzzle_canvas.delete("all")
        for widget in puzzleframe.winfo_children():
            if isinstance(widget, Entry):
                widget.destroy()

    
    SquareSide=int(420/GridSize)
 
    for i in range(GridSize+1):
        j=(i*SquareSide) + 5
        if i==0 or i==GridSize:
            widthline= 3
        else:
            widthline=1
        if GridSize==8:    
            puzzle_canvas.create_line(5,j,420,j,width=widthline)
            puzzle_canvas.create_line(j,5,j,423,width=widthline)
        else:   
            puzzle_canvas.create_line(5,j,425,j,width=widthline)
            puzzle_canvas.create_line(j,5,j,425,width=widthline)
    EntryHeightWidth = int(400/GridSize)-5
    SquareHeightWidth= int(420/GridSize)
#  Create the entry fields in the puzzle grid - The Entry Field descriptions are held in a list for later access the input into these fields.
    Entry_Names.clear()
    for i in range(NoOfSquares):
        EntryfieldDesc = Entry(puzzleframe,  justify="center",relief=FLAT, font ="Helvetica 18 bold",validate="focusout", validatecommand=callback)
        EntryfieldDesc.place(x= 10 + SquareHeightWidth*math.fmod(i,GridSize),y=10  + SquareHeightWidth*math.floor(i/GridSize),height = EntryHeightWidth, width = EntryHeightWidth)
        Entry_Names.append(EntryfieldDesc)
        
       
# This function is called to initialise the puzzle array to set the edges of the grid to 2
def Create_Puzzle_Array():
   
    Puzzle_Array.clear()            # empty the puzzle array of any old data  
    for i in range(NoOfSquares):
        array_element = {"top":0,"right":0,"bottom":0,"left":0,"chr":0,"original":0,"squares":[]}
        if i < GridSize:
            array_element["top"] = 2
        if math.fmod(i,GridSize) == GridSize -1:
            array_element["right"] = 2
        if i > (NoOfSquares - GridSize -1):
            array_element["bottom"] = 2
        if math.fmod(i,GridSize) == 0:
            array_element["left"] = 2
        Puzzle_Array.append(array_element)
        

# This function is called when the Draw button is clicked to start outline drawing
def Draw():
    global  drawing_enabled, puzzle_checked
    Draw_button.focus()
# set the cursor on the grid to a cross
    
    puzzle_canvas.config(cursor="tcross")

# enable the mouse left click event to trigger the 'leftclick' function when over the grid canvas 
    puzzle_canvas.bind("<Button-1>", leftclick)

# enable drawing of outline
    drawing_enabled = True 

# disable the Check and Solve buttons   
    Check_button['state']=DISABLED
    Solve_button['state']=DISABLED
# clear the 'squares' list in the puzzle array
    for i in range(NoOfSquares):
        Puzzle_Array[i]["squares"].clear()
# reset the puzzle checked condition
    puzzle_checked = False


# This function is called during the Outline drawing when the mouse left button is clicked
def leftclick(event):
    global delete_line,drawing_enabled
    if drawing_enabled == False: return
    cursorx = event.x 
    cursory = event.y 
# get coordinates relative to top left hand corner of grid
    x = cursorx      
    y = cursory 
# test if cursor on edge of grid and if so ignore
    if x < 6 or x > 414 or y < 6 or y > 414: return
# if cursor is to near the corner of a square then ignore.  Only accept a side when the cursor is
# clearly nearer to the middle of a side.
    remx=math.fmod(x,SquareSide)
    remy=math.fmod(y,SquareSide)
    margin=SquareSide-5
    if (remx < 10 and remy < 10) or (remx < 10 and remy > margin) or (remx > margin and remy <10) or (remx > margin and remy > margin): return
# determine which squares and sides that the cursor is on

    column = int(math.floor(x/SquareSide))
    row = int(math.floor(y/SquareSide))
    if remx < 10:
        square1 = (GridSize*row) + column - 1
        side1 = "right"
        square2 = square1+1
        side2 = "left"
    if remy < 10:
        square1 = (GridSize*row) + column 
        side1 = "top"
        square2 = square1 - GridSize
        side2 = "bottom"  
    if remx > margin:
        square1 = (GridSize*row) + column 
        side1 = "right"
        square2 = square1+1
        side2 = "left"
    if remy > margin:
        square1 = (GridSize*(row +1)) + column 
        side1 = "top"
        square2 = square1 - GridSize
        side2 = "bottom"   
# Find the status of these side in the two squares of the puzzle array and toggle them.
    square_info = Puzzle_Array[square1]
    if side1 == "right":
# line tag given to outlined sideof a grid square to enable the line to be removed later
        outline_status = square_info["right"]
        if outline_status == 0:
            square_info["right"] = 1
            delete_line=False
        else:
            square_info["right"] = 0
            delete_line=True
    else:
        outline_status = square_info["top"]
        if outline_status == 0:
            square_info["top"] = 1
        else:
            square_info["top"] = 0
    Puzzle_Array[square1] = square_info 
    square_info = Puzzle_Array[square2]
    if side2 == "left":
        outline_status = square_info["left"]
        if outline_status == 0:
            square_info["left"] = 1
        else:
            square_info["left"] = 0
    else:
        outline_status = square_info["bottom"]
        if outline_status == 0:
            square_info["bottom"] = 1
            delete_line = False
        else:
            square_info["bottom"] = 0
            delete_line=True
    Puzzle_Array[square2] = square_info 
    if remx < 10 or remx > margin:
        DrawSideOutline(square1,"right")
    else:
        DrawSideOutline(square2,"bottom")
    Check_button["state"]=NORMAL
    

# This function is called by the Clear button to start a new puzzle
# It clears any outline and any numbers in the grid
# and resets the puzzle array to initial conditions.
def Clear():

    Clear_grid()
    Create_Puzzle_Array()
    puzzle_canvas.config(cursor="arrow")
    Check_button['state']=DISABLED
    Save_button['state']=DISABLED
    Solve_button['state']=DISABLED
    Puzzle_Name['text']=''

# Function to clear any outline and delete data in Entry fields
def Clear_grid():
    global delete_line
    delete_line=True
    for SquareNumber in range(NoOfSquares):
        for Side in Sides:
           DrawSideOutline(SquareNumber,Side)
    for widget in puzzleframe.winfo_children():
        if isinstance(widget, Entry):
            widget.delete(0,END) # Clear an entry field
            widget.configure(font="Helvetica 14 normal")
    
# This function is called by the Save button to save the puzzle to a file in json format
def Save():
    global filetype
    Save_button.focus()
    path = filedialog.asksaveasfilename(title='Save the Suguru Puzzle',initialdir=puzzle_path,filetypes=[("Suguru File",'*'+ filetype)],defaultextension=filetype)
    if path=='':return  # cancel button clicked on Save As window
        
    file = open(path,"w")
    data = json.dumps(Puzzle_Array)
    file.write(data)
    file.close()
    
    filename=path[path.rfind('/')+1:len(path)][0:-5]  # get the filename from the path
    Puzzle_Name['text']=filename
    messagebox.showwarning("Saved Puzzle", filename + " saved")

""" 
This function is called by the Load button to load a saved puzzle
The saved file contains the Puzzle Array in json format

"""
def Load():
 
    global delete_line,puzzle_checked,Puzzle_Array
    Load_button.focus()
    path = filedialog.askopenfilename(title='Load a Suguru Puzzle',initialdir=puzzle_path,filetypes=[("Suguru File","*"+filetype)],defaultextension=filetype)
    if path=='':return  # cancel button clicked on file select window
    Clear_grid()
    file = open(path,"r")
    Puzzle_Array = json.loads(file.readline()) 
    file.close()
 
# Unpack the puzzle array into the grid - the outline of each square first and then the number in that square

    delete_line=False
    for SquareNumber in range(NoOfSquares):
        square_info=Puzzle_Array[SquareNumber]
        for Side in Sides:
            if square_info[Side]:
                DrawSideOutline(SquareNumber,Side)
        y=square_info["chr"] 
        if y != 0:
            Entry_Names[SquareNumber].delete(0,END)
            Entry_Names[SquareNumber].insert(0,y)
   
    Save_button['state']=NORMAL
    Check_button['state']=NORMAL
    Solve_button['state']=NORMAL
    Print_button['state']=NORMAL
    puzzle_checked=True
# Get the puzzle name without the filetype
    filename=path[path.rfind('/')+1:len(path)][0:-5]   
    Puzzle_Name['text']=filename
                 
# This function is called to solve the Suguru puzzle
def Solve():
    
# Set the puzzle array 'original' key value
    for i in range(NoOfSquares):
        square_info = Puzzle_Array[i]
        if square_info["chr"] !=0:
            square_info["original"]=1
            Puzzle_Array[i]=square_info
    Solve_button.focus()
    result=sol.puzzle_solve(Puzzle_Array) # Call the puzzle solving module
    if isinstance(result,int):
        if result ==1:
            messagebox.showerror(title="Error",message="Invalid Puzzle - Cannot solve it")
            return
        if result == 2:
            messagebox.showerror(title="Error",message="Invalid Puzzle - No Solution ")
            return
        if result == 3:
            messagebox.showerror(title="Error",message="It was not found possible to solve this puzzle.")
            return
    InsertNumbers()
""" 
The following function is called from the Print button to print the Suguru puzzle.
First extract an image from the screen to print.
To do this we need to know the position of the window on the screen
and then screen grab the puzzle section of the screen.
Second the image is saved to a temporary file on hard memory.
Then we need to print image from the file.
"""
def PrintPuzzle():
    
    Print_button.focus()
    if not messagebox.askyesno(None,"Did you mean to click the 'Print' button?",default = 'no'):return

# Constants for GetDeviceCaps
#
#
# HORZRES / VERTRES = printable area
#
    HORZRES = 8
    VERTRES = 10
#
# PHYSICALWIDTH/HEIGHT = total area
#
    PHYSICALWIDTH = 110
    PHYSICALHEIGHT = 111

    dim=mainwindow.winfo_geometry()
    xorigin_start=(dim.find("+"))+1
    xorigin_end=dim.index("+",xorigin_start+1)
    xorigin=int(dim[xorigin_start:xorigin_end])
    yorigin=int(dim[xorigin_end+1:])
    puzzle_image = ImageGrab.grab(bbox=(15 + xorigin,70+yorigin,450+xorigin,500+yorigin))
    file_name = 'puzzle_image.jpg'
    path=os.path.join(puzzle_path,file_name)
    if os.path.exists(path):
        os.remove(path)
    puzzle_image.save(path)  # save the image to a temporarty file called 'puzzle_image.jpg'
    
    printer_name = win32print.GetDefaultPrinter () 
    
#
#  You can only write a Device-independent bitmap
#  directly to a Windows device context; therefore
#  we need (for ease) to use the Python Imaging
#  Library to manipulate the image.
#
#  Create a device context from a named printer
#  and assess the printable size of the paper.
#
    hDC = win32ui.CreateDC ()
    hDC.CreatePrinterDC (printer_name)
    printable_area = hDC.GetDeviceCaps (HORZRES), hDC.GetDeviceCaps (VERTRES)
    printer_size = hDC.GetDeviceCaps (PHYSICALWIDTH), hDC.GetDeviceCaps (PHYSICALHEIGHT)
#
#  Open the image and work out how much to multiply
#  each pixel by to get it on the page using 0.4 of the page width 
#
    bmp = Image.open (path)
   
    scale = 0.6 * printable_area[0] / bmp.size[0]
#
#  Start the print job, and draw the bitmap to
#  the printer device at the scaled size.
#
    hDC.StartDoc (path)
    hDC.StartPage ()
      
    dib = ImageWin.Dib (bmp)
    scaled_width, scaled_height = [int (scale * i) for i in bmp.size]
       
    x1 = int ((printer_size[0] - scaled_width) / 2)
    y1 = int ((printer_size[1] - scaled_height) / 2)
    x2 = x1 + scaled_width
    y2 = y1 + scaled_height
    dib.draw (hDC.GetHandleOutput(), (x1, y1, x2, y2))

    hDC.EndPage ()
    hDC.EndDoc ()
    hDC.DeleteDC ()
    os.remove(path)

# This function is called to delete a saved puzzle
def Delete():
    global del_combowin
    Delete_button.focus()
    del_combowin=Toplevel(mainwindow)
    del_combowin.attributes('-toolwindow', True) # remove maximise and minimise icons
    del_combowin.title("")
    del_combowin.geometry("200x200+300+300")
    label1=Label(del_combowin,text="Select puzzle to delete")
    label1.pack(pady=3)
    files = os.listdir(puzzle_path)
    puzzle_list=[]
    for x in files:
        puzzlename=x[0:-5]
        puzzle_list.append(puzzlename)
    puzzle_file=StringVar()
    combo1=ttk.Combobox(del_combowin,values=puzzle_list,textvariable=puzzle_file)
    combo1.pack()
    combo1.current(0)
    combo1.focus()
    OKbutton = Button(del_combowin,text="OK",command= lambda: OKDelete(puzzle_file.get()),width=8)
    Cancelbutton=Button(del_combowin,text="Cancel",command=lambda: del_combowin.destroy(),width=8)
    OKbutton.pack(pady=3)
    Cancelbutton.pack(pady=3)
    
    del_combowin.mainloop()
# This function handles the deletion of a puzzle after the OK button has been clicked on the Delete Puzzle
# dialog window
def OKDelete(selected_file):
    global del_combowin
    choice=messagebox.askquestion("Delete Puzzle", "Are you sure you want to delete " + selected_file,default='no')
    if choice == 'no':
        del_combowin.destroy()
        return 
    filename = selected_file + filetype
    path= os.path.join(puzzle_path,filename)
    if os.path.exists(path):
        os.remove(path)
        del_combowin.destroy()
        messagebox.showwarning("Delete File ",selected_file + " deleted")
        if Puzzle_Name['text']== selected_file:         # if the puzzle being deleted is the one shown in the window then 
            Clear()                                          # clear it down.          
            
    else:
        messagebox.showerror("","Puzzle "+ selected_file + " not found")

def Check():
    global puzzle_checked,drawing_enabled
#   if puzzle_checked: return # Failsafe - don't check puzzle if it is unchanged 
#  Check for unconnected line vertical line
    for index in range(NoOfSquares):
        square_info=Puzzle_Array[index]
        index1 = index+1
        if index1 < NoOfSquares: square_info_next=Puzzle_Array[index1]
        index1= index+GridSize
        if index1 < NoOfSquares:square_info_below=Puzzle_Array[index1]
        index1 = index-1
        if index1 >= 0 :square_info_previous=Puzzle_Array[index1]
        index1= index-GridSize
        if index1 >= 0 :square_info_above=Puzzle_Array[index1]
        if square_info["right"]== 1:
            if square_info["bottom"]==2:  #one of the bottom row of squares?
                if square_info["top"] !=0: continue
                if square_info_next["top"]!=0:continue
                if square_info_above["right"] !=0: continue
                messagebox.showerror("Error","Unconnected vertical line in bottom row ")
                return
            if square_info["top"]==2:   #one of the top row of squares
                if square_info["bottom"] !=0: continue
                if square_info_next["bottom"]!=0:continue
                if square_info_below["right"] !=0: continue
                messagebox.showerror("Error","Unconnected vertical line in top row ")
                return
            
            if (square_info["bottom"]!=0 or square_info_next["bottom"]!=0 or square_info_below["right"]!=0) and \
                (square_info["top"]!=0 or square_info_next["top"]!=0 or square_info_above["right"]!=0): continue
            messagebox.showerror("Error","Unconnected vertical line")
            return
#  Check for unconnected line horizontal line
    for index in range(NoOfSquares):
        square_info=Puzzle_Array[index]
        index1 = index+1
        if index1 < NoOfSquares: square_info_next=Puzzle_Array[index1]
        index1= index+GridSize
        if index1 < NoOfSquares:square_info_below=Puzzle_Array[index1]
        index1 = index-1
        if index1 >= 0 :square_info_previous=Puzzle_Array[index1]
        index1= index-GridSize
        if index1 >= 0 :square_info_above=Puzzle_Array[index1]

        if square_info["bottom"]== 1:
            if square_info["left"]==2:  #one of the leftmost column of squares?
                if square_info["right"] !=0: continue
                if square_info_next["bottom"]!=0:continue
                if square_info_below["right"] !=0: continue
                messagebox.showerror("Error","Unconnected horizontal line in leftmost column")
                return
            if square_info["right"]==2:   #one of the top row of squares
                if square_info["left"] !=0: continue
                if square_info_previous["bottom"]!=0:continue
                if square_info_below["left"] !=0: continue
                messagebox.showerror("Error","Unconnected horizontal line in rightmost column")
                return
            
            if (square_info["right"]!=0 or square_info_next["bottom"]!=0 or square_info_below["right"]!=0) and \
                (square_info["left"]!=0 or square_info_previous["bottom"]!=0 or square_info_below["left"]!=0): continue
            messagebox.showerror("Error","Unconnected horizontal line")
            return   

# Save a temporary copy of the puzzle array in case an error is found and the puzzle
# array needs to be restored
    
    Copy_Puzzle_Array = Puzzle_Array.copy()  
    
# Process each grid square to see if it is in an outline of not more than 5 squares and save a list 
# of the squares in the outline in the same squares in the puzzle arrary
    for index in range(NoOfSquares):
        square_info=Puzzle_Array[index]
        if len(square_info["squares"]) != 0:
            continue
# If the square is totally outlined then set the square number into squares as the single
# square in the outline
        if square_info["right"] !=0 and  square_info["left"] !=0 \
        and  square_info["top"] !=0 and square_info["bottom"] !=0:
            square_info["squares"].append(index)
            Puzzle_Array[index] = square_info
            continue
# Start to find all the squares in the outline and put them in a list
        squares_in_outline = []
        squares_in_outline.append(index)
        index1 = index
        while square_info["right"]== 0:
            index1 +=1
            if index1 not in squares_in_outline: 
                squares_in_outline.append(index1)
            if len(squares_in_outline) > 5:
                Show_Puzzle_Error("More than 5 squares in outline")
                return  
            square_info = Puzzle_Array[index1]
        squares_so_far =squares_in_outline.copy()
# Make the following code repeat until there is no change in the no. of squares in the outline
        no_of_squares_in_outline=1        # set arbitrary values to get into while loop
        final_no_of_squares_in_outline=0
        while no_of_squares_in_outline != final_no_of_squares_in_outline:
            no_of_squares_in_outline=len(squares_in_outline)
# Look for squares below existing squares in outline
            for square_number in squares_so_far:
                square_info = Puzzle_Array[square_number]    
                square_below=square_number+GridSize
                while square_info["bottom"]== 0: 
                    if square_below not in squares_in_outline:
                        squares_in_outline.append(square_below)
                    if len(squares_in_outline) > 5:
                        Show_Puzzle_Error("More than 5 squares in outline")
                        return
                    square_info = Puzzle_Array[square_below]
                    square_below=square_below+GridSize
            squares_so_far = squares_in_outline.copy()
# Look for squares to the left of existing squares in the outline 
            for square_number in squares_so_far:
                square_info = Puzzle_Array[square_number]
                square_left=square_number-1
                while square_info["left"]== 0:                    
                    if square_left not in squares_in_outline:
                        squares_in_outline.append(square_left)
                    if len(squares_in_outline) > 5:
                        Show_Puzzle_Error("More than 5 squares in outline")
                        return
                    square_info = Puzzle_Array[square_left]
                    square_left=square_left-1
# Look for squares to the right of existing squares in the outline
            squares_so_far = squares_in_outline.copy()
            for square_number in squares_so_far:
                    square_info = Puzzle_Array[square_number]
                    square_right=square_number+1
                    while square_info["right"]== 0:                    
                        if square_right not in squares_in_outline:
                            squares_in_outline.append(square_right)
                        if len(squares_in_outline) > 5:
                            Show_Puzzle_Error("More than 5 squares in outline")
                            return
                        square_info = Puzzle_Array[square_right]
                        square_right=square_right+1
            squares_so_far =squares_in_outline.copy()
            final_no_of_squares_in_outline=len(squares_in_outline)
        
# store the square numbers in the 'squares' dictionary item in of each the outlined
# puzzle array squares

        for square_number in squares_in_outline:
            square_info = Puzzle_Array[square_number]
            square_info["squares"] = squares_in_outline
            Puzzle_Array[square_number] = square_info
    for i in range(NoOfSquares):
        square_info=Puzzle_Array[i]
        if len(square_info["squares"]) == 0:
            Show_Puzzle_Error("Program Error - not all squares in an outline")
            return  
    if not Check_Numbers(): return               
# The next line is only reached if all the outlines and numbers are ok                                            
    messagebox.showwarning("Success","The Puzzle layout is valid")
    puzzle_checked=True
    drawing_enabled = False
    puzzle_canvas.config(cursor="arrow")
    Save_button['state']=NORMAL
    Solve_button['state']=NORMAL
    Print_button['state']=NORMAL
    Check_button['state']=DISABLED
          
        
# This function is called to issue error message during the Check button processing
def Show_Puzzle_Error(Errormess):
    messagebox.showerror('Error',Errormess)
    Puzzle_Array = Copy_Puzzle_Array

# This function is called to check that the numbers in the grid are valid - If so return True - if not return False
        
def Check_Numbers():
    
    List1 =['1','1 2','1 2 3','1 2 3 4','1 2 3 4 5']
    ValidCharacters=['1','2','3','4','5']
# Get the current numbers into the puzzle array
    Copy_Puzzle_Array=Puzzle_Array
    for SquareNumber in range(NoOfSquares):
        square_info = Puzzle_Array[SquareNumber]

        
        Character = Entry_Names[SquareNumber].get()
        Character=Character.strip()  # remove any white characters
        Entry_Names[SquareNumber].delete(0,END) # and restore square contents
        Entry_Names[SquareNumber].insert(0,Character)
        if Character == '':
            square_info["chr"]=0
            
        else:
# Check if the character is a valid number between 1 and 5 
 
            if Character not in ValidCharacters:
                Show_Puzzle_Error("Invalid Character in Puzzle")
                return False
            Number = int(Character)
            square_info["chr"] = Number
        Puzzle_Array[SquareNumber]=square_info
# ensure that number is not in the outline more than once       
    for SquareNumber in range(NoOfSquares):
        square_info = Puzzle_Array[SquareNumber]
        Number = square_info["chr"]
        if Number==0: continue
        squares= square_info["squares"]
# The valid numbers in an outline depend on the size of the outline. Calculate a list of the valid numbers in the outline for this square
        index= len(squares)-1
        string1 = List1[index]
# convert string to a list of integers
        list1 = list(string1.split())
        ValidNumbers = list(map(int,list1)) 
        if Number in ValidNumbers:
            outline_squares = square_info["squares"]
            for square in outline_squares:
                if square ==SquareNumber:
                    continue
                other_square_info = Puzzle_Array[square]
                other_chr=other_square_info["chr"]
                if other_chr==Number:
                    Show_Puzzle_Error("Duplicate numbers in an outline")
                    return False
        else:
            Show_Puzzle_Error("Invalid character or number in puzzle grid")
            return False
    return True    
        

# This function is called to draw a bold single side line of a square into an outline in the grid 
# when the mouse is clicked according to it status in the puzzle array.  When creating the line it is given
# a tag which is used to delete the line if it is clicked again
def DrawSideOutline(SquareNumber,Side):
    global delete_line,puzzle_checked
    Check_button['state']=NORMAL
    Save_button['state']=DISABLED
    puzzle_checked = False
    linetag = Side + str(SquareNumber)
    if delete_line:
            puzzle_canvas.delete(linetag)
            return
# Calculate the coordinates of the side of the square and draw it on the canvas    
    column = math.fmod(SquareNumber,GridSize)
    row = math.floor(SquareNumber/GridSize)
    if Side == "right":
        x1=((column+1)*SquareHeightWidth) + 5 
        x2 = x1
        y1= ((row)*SquareHeightWidth) + 5
        y2 = y1+SquareHeightWidth
    if Side == "bottom":
        x1=((column)*SquareHeightWidth) +5 
        x2 = x1 + SquareHeightWidth
        y1= ((row +1)*SquareHeightWidth) +5 
        y2 = y1
    puzzle_canvas.create_line(x1,y1,x2,y2,width=3,tag=linetag)
 
# This function inserts the numbers into the grid after the Solve function has solved the puzzle setting
# the font to bold if it is one of the original numbers
def InsertNumbers():
    for square in range(NoOfSquares):
        square_info = Puzzle_Array[square]
        Number=str(square_info["chr"])
        
        Entry_Names[square].delete(0,END)     # clear existing Entry field in square
        Entry_Names[square].insert(0,Number)
        if square_info["original"]==1:
            Entry_Names[square].configure(font="Helvetica 18 bold")
        else:
            Entry_Names[square].configure(font="Helvetica 14 normal") 

# The following call back function is called whenever an entry field is changed.
def callback():
    global puzzle_checked
    Save_button['state']=DISABLED
    Solve_button['state']=DISABLED
    Check_button['state']=NORMAL
    puzzle_checked=False

# This function is called when the Size combobox is changed
def SizeComboBoxChanged(event):
    global GridSize, OldGridSize,NoOfSquares,puzzle_path,filetype
    OldGridSize=GridSize
    Size=puzzle_size.get()  # get the Size of the Puzzle
    GridSize=int(Size[0:1]) # grid size is 5,6,7 or 8
    NoOfSquares=GridSize**2
    Create_Puzzle_Array()   # refresh the puzzle array
    DrawGrid()
    puzzle_canvas.config(cursor="arrow")
    Check_button['state']=DISABLED
    Save_button['state']=DISABLED
    Solve_button['state']=DISABLED
    Puzzle_Name['text']=''
    
# Change the path to the save/load folder
    Folder='SuguruPuzzles'+ str(GridSize)
    appdata=os.getenv('LOCALAPPDATA')
    folder_path= os.path.join(appdata,"SuguruSolver")
    puzzle_path= os.path.join(folder_path,Folder)
    path = Path(puzzle_path)
    if not os.path.exists(puzzle_path):
        os.mkdir(puzzle_path)
# Set the filetype for this type of puzzle when saved
    filetype='.sug'+str(GridSize)

# The following function is far quicker than using tkinter quit() or exit()
def quitapp():
    mainwindow.destroy()
    
# End of Function Code
# Main code
Sides = ["right","bottom"]
filetype='.sug5'
mainwindow=Tk()
mainwindow.title("Solve a Suguru Puzzle")
mainwindow.geometry("550x550")
mainwindow.resizable(False,False)
sizeframe=Frame(mainwindow, height=30, width=100)
sizeframe.place(x=30,y=10)
puzzleframe=Frame(mainwindow,height=430,width=430)
puzzleframe.place(x=10,y=40)
puzzleframe.bind("<Button-1>", leftclick)           # initiate response function to handle mouse left click button.
buttonframe=Frame(mainwindow,height=218, width= 100)
buttonframe.place(x=460, y=40)
Drawframe=Frame(mainwindow,height= 50, width=220)
Drawframe.place(x=30,y=480)
PuzzleNameframe=Frame(mainwindow,height=30,width=120,relief=RIDGE, borderwidth=3)
PuzzleNameframe.place(x=258,y=490)
sizevar=StringVar()
sizelabel=Label(sizeframe,height=1,width=3,textvariable=sizevar)
sizevar.set('Size:')
sizelabel.place(x=0,y=0)
# Set up a Size combo box to call a function when it is changed
sizes=['5x5','6x6','7x7','8x8']
puzzle_size=StringVar()
sizecombo=ttk.Combobox(sizeframe,values=sizes,textvariable=puzzle_size,width=3)
sizecombo.place(x=40,y=2)
sizecombo.focus()
sizecombo.current(0)
sizecombo.bind("<<ComboboxSelected>>",SizeComboBoxChanged)
# Draw the intial grid
puzzle_canvas=Canvas(puzzleframe, height=425,width=425,bg="white")
puzzle_canvas.place(x=0,y=0)
OldGridSize=0
GridSize= 5
NoOfSquares=GridSize*GridSize
DrawGrid()
# Ensure there is a folder for saving puzzles in 'Appdata\Local\SuguruSolver\SuguruPuzzles + GridSize and put the full path in 'puzzle_path'
Folder='SuguruPuzzles'+ str(GridSize)
appdata=os.getenv('LOCALAPPDATA')
folder_path= os.path.join(appdata,"SuguruSolver")
path = Path(folder_path)
print(folder_path)
if os.path.exists(folder_path):
    print(folder_path + ' exists')
if not  os.path.exists(folder_path):
       os.mkdir(folder_path)
puzzle_path= os.path.join(folder_path,Folder)
path = Path(puzzle_path)
if not os.path.exists(puzzle_path):
       os.mkdir(puzzle_path)
# Create the buttons    
Clear_button = Button(buttonframe, text="Clear", command=Clear,width=8)
Clear_button.place(x=10,y=10)
Clear_button['state']=NORMAL # change this to DISABLED later
Solve_button = Button(buttonframe, text="Solve", command=Solve,width=8)
Solve_button.place(x=10,y=40)
Solve_button['state']=DISABLED
Save_button = Button(buttonframe, text="Save", command=Save,width=8)
Save_button.place(x=10,y=70)
Save_button['state']=NORMAL # change this to DISABLED later
Load_button = Button(buttonframe, text="Load", command=Load,width=8)
Load_button.place(x=10,y=100)
Delete_button = Button(buttonframe, text="Delete", command=Delete,width=8)
Delete_button.place(x=10,y=130)
Quit_button = Button(buttonframe, text="Quit", command=quitapp,width=8)
Quit_button.place(x=10,y=160)
Print_button = Button(buttonframe, text="Print", command=PrintPuzzle,width=8)
Print_button.place(x=10,y=190)
Print_button['state']=DISABLED
Draw_button = Button(Drawframe, text="Draw", command=Draw,width=7,height=2)
Draw_button.place(x=25,y=10)
Check_button = Button(Drawframe, text="Check", command=Check,width=7,height=2)
Check_button.place(x=90,y=10)
Check_button['state']=DISABLED

# Add a Label to put name of puzzle in, if it is loaded or saved.
Puzzle_Name=Label(PuzzleNameframe,width=12)
Puzzle_Name.pack(padx=5,pady=5)

# Intialise the puzzle array
Create_Puzzle_Array()

mainwindow.mainloop()
