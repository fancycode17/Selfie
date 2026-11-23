import json
from colorama import Fore, Style, init
from typing import Any
from datetime import datetime
from dataclasses import dataclass, asdict

#TODO: add undo/redo functions
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
        selfie: State = self.curState
        if len(self.__history) == 0 or selfie != self.__history[-1].state:
            #avoid adding to history if no changes have been made
            self.__history.append(Snapshot(self.timestamp(), self.curState))
            self.log(f'Selfie object state successfully saved as: {selfie}', color='GREEN')
        else:
            self.log(f'Warning: Selfie object state not saved - matches previous state: {selfie}', color='YELLOW')

    def package(self, output_file: str) -> None: #write history to file
        with open(output_file, 'w') as file:
            try:
                json.dump([asdict(snapshot) for snapshot in self.__history], file, indent=4)
            except json.JSONDecodeError:
                self.log(f'Error: Selfie object history corrupted - packaging failed: {self.__history}.', color='RED')
                exit()

        self.log(f'Selfie object history packaged successfully to {output_file}.', color='GREEN')

    def timestamp(self):
        year = str(datetime.now().timetuple().tm_year)[2:]
        day = str(datetime.now().timetuple().tm_yday)
        min = str(datetime.now().timetuple().tm_min)
        hour = str(datetime.now().timetuple().tm_hour)
        sec = str(datetime.now().timetuple().tm_sec)
        timestamp = int(year + day + hour + min + sec)
        return timestamp