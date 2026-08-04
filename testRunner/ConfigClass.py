#Run wide settings, assigned by testRunner.py during startup and read by the rest of the runner.
pathToEngineExecutable = ""
pathToDumpLogs = None

#Directory the engine is told to write its own log into, via --logFile.
#Each test gets its own file in here so concurrent engine processes never share one log.
pathToEngineLogs = None

#How many test cases to run at once.
concurrency = 1
