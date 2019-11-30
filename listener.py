#############################
# Imports
#############################

import os, ctypes, psutil, time, json
from os import path

#############################
# Variable Definitions
#############################

data = open('config.json', "r")
config = json.load(data)

dropboxPath = config["dropboxPath"]
updateTime = config["updateTime"]
paths = config["paths"]

#############################
# Functions
#############################

def generateProcessDict():
	liteProcessList = {}
	for procID in psutil.pids():
		processObj = psutil.Process(procID)
		liteProcessList[procID] = processObj.name()
	return liteProcessList

def parseCommands(file):
    output = []
    if type(file) == str:
        if path.exists(file):
            f = open(file, "r")
            fileText = ""
            for lines in f:
                fileText += lines
                commandStrings = fileText.split(", ")
                for command in commandStrings:
                    command = command.split()
                    if len(command) > 0:
                        output.append({"task": command[0], "args": command[1:]})

            f.close()
        else:
            output.append({})

    return output

def process_exists(processName):
    output = False
    for key in processList:
        if processName.lower() in processList[key].lower():
            output = True
    return output

def getTxtFiles(directory):
    files = []
    if path.exists(directory):
        for file in os.listdir(directory):
            if ".txt" in file:
                files.append(file)

    return files

#############################
# Task Functions
#############################

def launch(program):
    output = ""
    if type(program) == str:
        try:
            os.startfile(program)
            output = "success"
        except OSError:
            output = "Failed to launch program"
    return output

def wait(ms):
    output = ""
    ms = int(ms)
    if type(ms) == int and ms > 1:
        time.sleep(ms/1000)
        output = "success"
    else:
        output = "invalid input"
    return output

def kill(program):
    output = ""
    if type(program) == str:
        os.system("taskkill /IM " + program + " /F")
        output = "success"
    else:
        output = "invalid input"
    return output

def shutdown(system):
	output = "success"
	os.system('shutdown -s')
	return output

def popup(message):
	output = ""
	if type(message) == str:
		ctypes.windll.user32.MessageBoxW(0, str(message), "Message from Amazon Alexa", 0)
		output = "success"
	else:
		output = "invalid input"
	return output


#############################
# Mappings
#############################

functions = {
    "launch": launch,
    "wait": wait,
    "kill": kill,
    "shutdown": shutdown,
	"popup": popup
    }

#############################
# Program Logic
#############################

print("Initializing...")
processList = generateProcessDict()

if(not process_exists("Dropbox.exe")):
    ctypes.windll.user32.MessageBoxW(0, "Could not find process for 'Dropbox.exe'", "Error", 0)
else:
    print("Dropbox process found")
    print("\n===========\n")

    fileList = getTxtFiles(dropboxPath)
    while True:
        for f in getTxtFiles(dropboxPath):
            if f not in fileList:
                commands = parseCommands(dropboxPath + "/" + f)

                for each in commands:
                    commandTask = each["task"]
                    commandArgs = each["args"]

                    print("Instruction: " + str(commands.index(each) + 1))
                    print("Task: " + commandTask)
                    print("Arguments: " + ", ".join(commandArgs))
                    print("\n===========\n")

                    if len(commandArgs) == 0:
                            # Checks if no argument is provided for function and generates a placeholder if needed
                            commandArgs.append("Placeholder")

                    if commandTask.lower() == "launch":
                            # Assuming an executible name is given as the first agument to launch, replaces name with file path
                            if not path.exists(commandArgs[0]):
                                    for key in paths:
                                            for arg in commandArgs:
                                                    if key.lower() == arg.lower():
                                                            commandArgs[commandArgs.index(arg)] = paths[key]
                
                    if commandTask.lower() == "popup":
                            msg =  " ".join(commandArgs)
                            commandArgs = []
                            commandArgs.append(msg)
			   
                    for key in functions:
                            # Call function with provided arguments
                        if key.lower() == commandTask.lower():
                            run = functions[key](commandArgs[0])
                            if run != "success":
                                print("Error: " + run)
                # Clean-up and remove instruction file
                os.remove(dropboxPath + "/" + f)
        # Update timer to lower stress on system
        time.sleep(updateTime)
