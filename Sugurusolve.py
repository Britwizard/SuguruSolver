'''Sugurusolve  - solve a Suguro puzzle
Version 1 - Initial coding
Version 2 - Modified to handle 5,6,7,8 square sided puzzles
Version 3 - remove unnecessary global statements

This module is imported by the Suguru Solver
which calls the puzzle_solve(puzzle_array) function to solve the puzzle.
'puzzle_array' is a list of dictionary items that decribe the Suguru puzzle
'''

import math


# FUNCTIONS:

# This is the first function called in this modules and calls all the other functions directly or indirectly
# and returns either a solved puzzle array or an error indidcator 1 to 3

def puzzle_solve(puzzle_array):
    global wrong_value,array_change,Recalculate,NoOfSquares,GridSize,Number_List,Candidates_array,Puzzle_Array
    # Global variables
    Candidates_array=[]
    Number_List=[]
    Puzzle_Array=puzzle_array
    wrong_value=False
    array_change=False
    Recalculate=False
    NoOfSquares=len(Puzzle_Array)
    GridSize=int(math.sqrt(NoOfSquares))
    #Local Variables
    Stack=[]
# Create a list of all the numbers in the puzzle (including 0 for unsolved squares)
# and Initialise Candidates_array
 
    for i in range(NoOfSquares):
        Number_List.append(puzzle_array[i]["chr"])
        Candidates_array.append([0])
 
        
# Attempt to solve the puzzle without use of the stack   
    Basic_Solve()
    if not 0 in Number_List: return(Populate(puzzle_array))  # solution found
      
    if wrong_value:
            return 1              # invalid puzzle - no candidates in a square on first pass
        
# The following code is the 'contingency code' described in the proram design
# It is for puzzles that are not solved by the Basic Solve
# It uses a brute force method of solving the puzzle by trying out values in 
# squares that have two candidates. It uses a stack to save the condition of the number list
# and candidate array before the trial and restores them if the trial fails to get any 
# candidates for a square.
    
    Result = Find_trial_pair()
    while Result["pairfound"] and 0 in Number_List:
        Number_List_copy = Number_List.copy()
        Candidates_array_copy = Candidates_array.copy()
        square = Result["square"]
        pair = Result["pair"]
        stack_item = {"Number_List_copy":Number_List_copy,"Candidates_array_copy":Candidates_array_copy,"pair":pair, "square":square,"Indicator":1}  #Indicator 1 shows first candidate in pair trialled. 2 for second.
        Stack.append(stack_item)
        first_value=pair[0]
        Number_List[square]=first_value
        Basic_Solve()
        if not 0 in Number_List: return(Populate(puzzle_array))  # solution found
        if wrong_value:
            Stack[-1]["Indicator"]=2
            Number_List=Stack[-1]["Number_List_copy"]
            Candidates_array=Stack[-1]["Candidates_array_copy"]
            second_value=Stack[-1]["pair"][1]
            square=Stack[-1]["square"]
            Candidates_array[square]=[second_value]
            Number_List[square]=second_value
            Basic_Solve()
            if not 0 in Number_List: return(Populate(puzzle_array))  # solution found
            while wrong_value:           # second value wrong
                if len(Stack) == 1:
                     return 2          # No solution found
                Stack.pop()
                if Stack[-1]["Indicator"]==1:
                    Stack[-1]["Indicator"]=2
                    Number_List=Stack[-1]["Number_List_copy"]
                    Candidates_array=Stack[-1]["Candidates_array_copy"]
                    second_value=Stack[-1]["pair"][1]
                    square=Stack[-1]["square"]
                    Candidates_array[square]=[second_value]
                    Number_List[square]=second_value                          
                    Basic_Solve()    
                    if not 0 in Number_List: return(Populate(puzzle_array))  # solution found
  
        Result = Find_trial_pair()
    return 3                # pair not found   

'''
This function populates the candidate array with possible candidates for each square based on the rules.
Since it is possible(even likely) that a single candidates will arise for a number of squares the cycle is repeated
including using those candidates.  This cycle is repeated until no further single candidates are discovered.
When the function exits - If there are no more zero squares in the Number List 
the puzzle is solved.
'''
def Calculate_Candidates():
    global wrong_value,array_change
    List1 =[[1,2],[1,2,3],[1,2,3,4],[1,2,3,4,5]]
    array_change=True       # Force the first cycle of the calculation
    while array_change and 0 in Number_List:
        array_change = False
        wrong_value= False
        for i in range(NoOfSquares):
            candidate_list = Candidates_array[i]
            Number = Number_List[i]
            square_info=Puzzle_Array[i]
# Process the square that contains a number in the puzzle - put a list containing the number into the 
# candidates array if not already there.
            if Number !=0:
                if candidate_list != [Number]:                
                    Candidates_array[i] = [Number]
                    array_change=True
                continue
# Process a square that has only one square in the outline - this can only be 1
# Set it into candidate array as [1] if it is not already therand set the puzzle array to 1 if 
            squares=square_info["squares"]
            if len(squares)==1:
                numberList=[1]
                if candidate_list != numberList:
                    Candidates_array[i] = numberList
                    Number_List[i] = 1
                    array_change=True
                continue
# The following code produces an elimination list eg for a 3 square outline it generates the list [1,2,3]. This will
# be used to eliminate candidates.          

            index= len(squares)-2
            el_list = List1[index]
            elimination_list = el_list.copy()               # need to get an immutable copy otherwise List1 gets corrupted
# Now remove candidates from the elimination list if they are already in the outline.
            for square in squares:
                if square==i:continue
                Number= Number_List[square]
                if Number !=0:
                    if Number in elimination_list:
                        elimination_list.remove(Number)
# If there is square to the right that has a number remove it from the elimination list if it is 
# in the elimination list
            j=i+1
            if math.fmod(j,GridSize)!=0:               
                Number = Number_List[j]
                if Number in elimination_list:
                        elimination_list.remove(Number)    
# If there is square to the left that has a number remove it from the elimination list if it is 
# in the elimination list
            if math.fmod(i,GridSize)!=0:
                j=i-1              
                Number = Number_List[j] 
                if Number in elimination_list:
                        elimination_list.remove(Number)    
# If there is square above that has a number remove it from the elimination list if it is 
# in the elimination list
            if i > GridSize - 1:
                j=i-GridSize              
                Number = Number_List[j]
                if Number in elimination_list:
                        elimination_list.remove(Number)    
# If there is square below  that has a number remove it from the elimination list if it is 
# in the elimination list
            if i < NoOfSquares-GridSize:
                j=i+GridSize              
                Number = Number_List[j]
                if Number in elimination_list:
                        elimination_list.remove(Number)
# If there is square to upper left diagonal that has a number remove it from the elimination list if it is 
# in the elimination list
            if math.fmod(i,GridSize) !=0 and i > GridSize-1:
                j=i-GridSize-1              
                Number = Number_List[j]
                if Number in elimination_list:
                        elimination_list.remove(Number)    
    
# If there is square to upper right diagonal that has a number remove it from the elimination list if it is 
# in the elimination list
            j=i+1
            if math.fmod(j,GridSize) !=0 and i > GridSize-1:
                j=i-GridSize + 1              
                Number = Number_List[j] 
                if Number in elimination_list:
                        elimination_list.remove(Number)
# If there is square to lower left diagonal that has a number remove it from the elimination list if it is 
# in the elimination list
            if math.fmod(i,GridSize) !=0 and i < NoOfSquares-GridSize:
                j=i+GridSize-1              
                Number = Number_List[j]
                if Number in elimination_list:
                        elimination_list.remove(Number)    
# If there is square to lower right diagonal that has a number remove it from the elimination list if it is 
# in the elimination list
            j=i+1
            if math.fmod(j,GridSize) !=0 and i < NoOfSquares-GridSize:
                j=i+GridSize+1              
                Number = Number_List[j]
                if Number in elimination_list:
                        elimination_list.remove(Number)
# The numbers left in the elimination list are the candidates.
            candidates_list = elimination_list

# If there are no candidates then there is an error
            if len(candidates_list) == 0:
                wrong_value= True
                return
# If there is just one candidate then update the Puzzle array 
            if len(candidates_list) == 1:
                Number=candidates_list[0]
                Number_List[i] = Number
           
# Save candidates list in the candidates array
            if candidate_list != candidates_list:
                Candidates_array[i] = candidates_list
                array_change=True
                
def Process_Unique_Candidates():
    global Recalculate
    Recalculate = False
    unique_array_change= True
    while unique_array_change:
        unique_array_change = False
        for i in range(NoOfSquares):
            mut_candidates=Candidates_array[i]      # mutable version of candidates for square
            if len(mut_candidates)==1: continue
            candidates=mut_candidates.copy()        # immutable version of candidates for square
            squares=Puzzle_Array[i]["squares"]
            for square in squares:
                if square==i:continue
                other_candidates=Candidates_array[square]
                if len(other_candidates)==1:continue
                for other_number in other_candidates:
                    if other_number in candidates:
                        candidates.remove(other_number)
            if len(candidates)==1:
                unique_number = candidates[0]
                unique_array_change = True
                Recalculate=True
                Candidates_array[i]=candidates
                Number_List[i]=unique_number
                

def Basic_Solve():
    global Recalculate
    Recalculate=True
    while Recalculate:
        Calculate_Candidates()
        if wrong_value or 0 not in Number_List:break
                
        Process_Unique_Candidates()
        if wrong_value or 0 not in Number_List:break
        
        
        

# Find a pair of values in the Candidate array to try out as solutions for a square
def Find_trial_pair():
    for square in range(NoOfSquares):
        if len(Candidates_array[square])==2:
            pairlist = Candidates_array[square]
            pair=pairlist.copy()
            return_result={"pairfound": True,"pair":pair, "square":square}
            return return_result
    return_result = {"pairfound":False}
    return return_result
# Put numbers into the puzzle array 
def Populate(puzzle_array):

    for i in range(NoOfSquares):
        puzzle_array[i]["chr"]= Number_List[i]
    return puzzle_array