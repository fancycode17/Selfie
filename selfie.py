import json
from colorama import Fore, Style, init
from typing import Any, Literal
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

#TODO: add undo/redo functions
#TODO: add sudo-style insults for errors
'''json module info:
        dump = write to a file
        dumps = convert to JSON string
        load = load from file
        loads = load from string
    
    colorama module info:
        Fore = change color of text
        Style = Bold, Italic, etc.

'''

init(autoreset=True)

class InputError(Exception): ...
noneInt = int | None #Useful for type hints
noneStr = str | None #Useful for type hints
State = dict[str, Any] #Useful for type hints

@dataclass
class Snapshot:
    timestamp: int
    state: State

class Selfie:   
    def __init__(self, source_file: noneStr = None) -> None:
        self.__history: list[Snapshot] #declaring the type at the start prevents redefining of types
        self.__logs: list[str] = []
        self.__view = self.View(self) #Note that self.view won't work here as it will be deleted by the self.update function

        if source_file is not None: #if a source file from which to initialize history has been provided
            try:
                with open(source_file, 'r') as file:
                    self.__history = [Snapshot(**item) for item in json.load(file)]
                    self.update(index=-1) #set current state to most recent state in history
            except FileNotFoundError:
                self.log(f'Error: Selfie object initialization failed - source file \'{source_file}\' not found.', color='RED')
                exit()
            except json.JSONDecodeError:
                self.log(f'Error: Selfie object initialization failed - source file \'{source_file}\' contains invalid JSON.', color='RED')
                exit()
            except TypeError:
                self.log(f'Error: soure file \'{source_file}\' is corrupted.', color='RED')
                exit()
            except IndexError:
                self.log(f'Warning: source file \'{source_file}\' empty, initializing Selfie object with empty history.', color='YELLOW')
                self.__history = [Snapshot(self.timestamp(),{})]

        else:
            self.__history = [Snapshot(self.timestamp(),{})] #history of states

        self.log(f'Selfie object initialized successfully.', color='GREEN')

    def log(self, message, color:noneStr = '', bold:bool = True, hidden=False) -> None: #to simplify colored logs
        colorCommand: str
        boldCommand: str

        colorOptions = ['GREEN', 'YELLOW', 'RED']
        if color in colorOptions:
            colorCommand = getattr(Fore, color) #e.g. if color is 'GREEN' this returns Fore.GREEN
        elif color == '':
            colorCommand = ''
        else:
            raise InputError('Color parameter must be "GREEN", "YELLOW" or "RED".')

        if bold:
            boldCommand = Style.BRIGHT
        else:
            boldCommand = ''

        log = f'{colorCommand}{boldCommand}{message}'
        if not hidden:
            print(log)

        self.__logs.append(log)

    @property
    def curState(self) -> State: 
        '''return python dict of current state (not including hidden/private variables)'''
        params: State = {
            k:v
            for k, v in vars(self).items()
            if not k.startswith('_')
        }
        return params

    @property
    def history(self) -> list[Snapshot]: 
        '''self.__history should be used within the class instead.'''
        return self.__history.copy() #returns a copy to prevent edits from outside the class

    @property
    def logs(self) -> list[str]: 
        '''self.__logs should be used within the class instead.'''
        return self.__logs.copy() #returns a copy to prevent edits from outside the class

    @property
    def view(self):
        return self.__view

    def update(self, state: str = '{}', index: noneInt = None) -> None:
        '''
        Change current state to a state provided by the user or a previous state that has been stored in memory.
        '''
        current: State = self.curState
        new: State #prevents redefining of types

        if index is not None: #i.e. if it should update to a state in self.__history
            try:
                new = self.__history[index].state.copy()
            except TypeError:
                self.log(f'Error: Selfie object update failed - history corrupted (state is of type dict instead of str).', color='RED')
                exit()

        else: #i.e. if the user provides a new state for it to update to
            try:
                new = json.loads(state)
            except TypeError:
                self.log(f'Error: Selfie object update failed - JSON state provided must be of type str, bytes or bytearray, not dict.', color='RED')
                exit()
            except json.JSONDecodeError:
                self.log(f'Error: Selfie object update failed - state argument contains invalid JSON: {state}.', color='RED')
                exit()

        for key, value in new.items():
            if key.startswith('_'): #ignore private/hidden variables
                continue
            if key not in current.keys() or value != current[key]: 
                #don't set attribute that already exists with the same value
                setattr(self, key, value)

        for k in current.keys(): #delete variables not mentioned
            if k not in new.keys():
                delattr(self, k)

        self.log(f'Selfie object updated successfully.', color='GREEN')

    def save(self) -> None: #take a selfie and store it in history as json string
        state: State = self.curState
        if len(self.__history) == 0 or state != self.__history[-1].state:
            #avoid adding to history if no changes have been made
            self.__history.append(Snapshot(self.timestamp(), self.curState))
            self.log(f'Selfie object state successfully saved as: {state}', color='GREEN')
        else:
            self.log(f'Warning: Selfie object state not saved - matches previous state: {state}', color='YELLOW')

    def package(self, output_file: str) -> None: #write history to file
        with open(output_file, 'w') as file:
            try:
                json.dump([asdict(snapshot) for snapshot in self.__history], file, indent=4)
            except json.JSONDecodeError:
                self.log(f'Error: Selfie object history corrupted - packaging failed: {self.__history}.', color='RED')
                exit()

        self.log(f'Selfie object history packaged successfully to \'{output_file}\'.', color='GREEN')

    def timestamp(self):
        year = str(datetime.now().timetuple().tm_year)[2:]
        day = f'{datetime.now().timetuple().tm_yday:03d}'
        hour = f'{datetime.now().timetuple().tm_hour:02d}'
        min = f'{datetime.now().timetuple().tm_min:02d}'        
        sec = f'{datetime.now().timetuple().tm_sec:02d}'
        timestamp = int(year + day + hour + min + sec)
        return timestamp

    class View:
        '''
            Subclass to output attributes of a Selfie object (e.g. its history) in a way that is visually appealing to terminal users.
        '''
        def __init__(self, selfie):
            self.selfie = selfie

        def history(self, depth:int=9, startWith:Literal['newest', 'oldest'] = 'newest'):
            '''
                Neatly ouputs history up to a certain depth (depth + 1 items), the default being 10.
                The history may be outputted from oldest to newest entry or from newest to oldest entry based on the timestamp.

                History is outputted in the format:
                count_number - [time] on the [day] of [month], [year]:
                    State = [Snapshot.state]

                Where time is in the format hh:mm:ss
            '''
            order = -1 if startWith == 'newest' else 1
            count = 1
            for item in self.selfie.history[depth::order]: #10 most recent entries (reverse order = newest -> oldest)
                timestamp:str = str(item.timestamp)
                year = int('20'+timestamp[:2])
                daynum = int(timestamp[2:5]) #number of days that have passed in the year
                date = datetime(year, 1, 1) + timedelta(days=daynum - 1) #returns datetime object of current date based on current year and daynum 
                hour:str = timestamp[5:7] #not converted to int to preserve leading zeroes.
                min:str = timestamp[7:9] #not converted to int to preserve leading zeroes.
                sec:str = timestamp[9:11] #not converted to int to preserve leading zeroes.

                print(f'{count} - {hour}:{min}:{sec} on the {date.strftime('%d of %B, %Y')}:')
                print(f'\t State = {item.state}')
                print()
                count += 1