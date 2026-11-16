import json
from colorama import Fore, Style, init

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

noneInt = int | None #Useful for type hints
noneStr = str | None #Useful for type hints

class Selfie:
    def __init__(self, source_file: noneStr = None) -> None:
        self.__history: list[str] #prevents redefining of types

        if source_file is not None: #if a source file from which to initialize history has been provided
            try:
                with open(source_file, 'r') as file:
                    self.__history = json.load(file)
                    self.update(index=-1) #set current state to most recent state in history
            except FileNotFoundError:
                print(f'{Fore.RED}{Style.BRIGHT}Error: Selfie object initialization failed - source file \'{source_file}\' not found.')
                exit()
            except json.JSONDecodeError:
                print(f'{Fore.RED}{Style.BRIGHT}Error: Selfie object initialization failed - source file \'{source_file}\' contains invalid JSON.')
                exit()
            except IndexError:
                print(f'{Fore.YELLOW}{Style.BRIGHT}Warning: source file \'{source_file}\' empty, initializing Selfie object with empty history.')
                self.__history = []

        else:
            self.__history = [] #history of states

        print(f'{Fore.GREEN}{Style.BRIGHT}Selfie object initialized successfully.')

    @property
    def curState(self) -> dict: #return python dict of current state (not including hidden/private variables)
        params: dict = {
            k:v
            for k, v in vars(self).items()
            if not k.startswith('_')
        }
        return params

    @property
    def history(self):
        return self.__history
    
    def update(self, state: str = '{}', index: noneInt = None) -> None:
        current: dict = self.curState
        new: dict #prevents redefining of types

        if index is not None: #checks where to get new parameters from
            try:
                new = json.loads(self.__history[index])
            except json.JSONDecodeError:
                print(f'{Fore.RED}{Style.BRIGHT}Error: Selfie object update failed - history corrupted: {self.__history}.')
                exit()

        else:
            try:
                new = json.loads(state)
            except json.JSONDecodeError:
                print(f'{Fore.RED}{Style.BRIGHT}Error: Selfie object update failed - state argument contains invalid JSON: {state}.')
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

    def save(self) -> str: #take a selfie and store it in history as json string
        selfie: str = json.dumps(self.curState)
        if len(self.__history) == 0 or selfie != self.__history[-1]: 
            #avoid adding to history if no changes have been made
            self.__history.append(selfie)
            return f'{Fore.GREEN}{Style.BRIGHT}Selfie object state successfully saved as: {selfie}'
        else:
            return f'{Fore.YELLOW}{Style.BRIGHT}Warning: Selfie object state not saved - matches previous state.'   

    def package(self, output_file) -> str: #write history to file
        with open(output_file, 'w') as file:
            try:
                json.dump(self.__history, file, indent=4)
            except json.JSONDecodeError:
                print(f'{Fore.RED}{Style.BRIGHT}Error: Selfie object history corrupted - packaging failed: {self.__history}.')
                exit()

        return f'{Fore.GREEN}{Style.BRIGHT}Selfie object history packaged successfully to {output_file}.'