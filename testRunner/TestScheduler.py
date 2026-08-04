import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from TestCaseExecution import colour

#Runs the test cases of every test plan through a single pool of workers.
#The pool spans all plans rather than being rebuilt per plan, so a plan containing
#only a couple of test cases never leaves workers sitting idle.

def collectWorkItems(testPlans):
    workItems = []
    for plan in testPlans:
        #Sized up front so each result can be written back by index. Completion order
        #varies between runs, but the results keep the order the tests were discovered in.
        plan.testCaseResults = [None] * len(plan.testCaseExecutions)
        for index, testCase in enumerate(plan.testCaseExecutions):
            workItems.append((plan, index, testCase))

    return workItems

def warnOnDuplicateTestNames(workItems):
    #Log files are named after the test, so two tests sharing a name write to the same
    #file. Serially that was an overwrite, concurrently it's two engines writing at once.
    planNamesByTest = {}
    for plan, index, testCase in workItems:
        planNamesByTest.setdefault(testCase.getTestCaseName(), []).append(plan.testPlanName)

    for testName, planNames in planNamesByTest.items():
        if(len(planNames) <= 1):
            continue

        print(colour.YELLOW + "Warning: the test name '%s' is used by %i test cases (in %s). Their log files will collide."
            % (testName, len(planNames), ", ".join(planNames)) + colour.END)

def runTestCases(testPlans, flags=None, jobs=1):
    workItems = collectWorkItems(testPlans)
    totalCases = len(workItems)
    if(totalCases <= 0):
        print("No test cases were found to run.")
        return

    warnOnDuplicateTestNames(workItems)

    #Running serially, each test streams its output as it happens, as it always has.
    #Running concurrently that output would interleave, so it's buffered until the test ends.
    liveOutput = jobs <= 1
    for plan, index, testCase in workItems:
        testCase.liveOutput = liveOutput

    print("Running %i test cases across %i test plans, %i at a time." % (totalCases, len(testPlans), jobs))

    def runOne(workItem):
        plan, index, testCase = workItem
        #Wraps the whole call, not just the engine subprocess, so this is genuinely "how long
        #this test case took" as experienced by the scheduler - process spawn, run, log
        #copying and result parsing all included. perf_counter is monotonic and the highest
        #resolution clock available, well under the millisecond precision asked for.
        startTime = time.perf_counter()
        try:
            plan.testCaseResults[index] = testCase.execute(plan.baseSetupFile, flags)
        except Exception as e:
            #One test blowing up shouldn't take the rest of the run with it.
            testCase.log(colour.RED + "Test case %s raised an exception: %s" % (testCase.getTestCaseName(), e) + colour.END)
            plan.testCaseResults[index] = testCase.buildFailureResult(0, ["The test runner raised an exception: %s" % e])
        durationMs = (time.perf_counter() - startTime) * 1000.0
        plan.testCaseResults[index]["durationMs"] = durationMs

        return workItem

    completedCases = 0
    #Threads rather than processes. Each worker spends its time blocked in
    #subprocess.communicate(), which releases the GIL, and they share ConfigClass as is.
    with ThreadPoolExecutor(max_workers=jobs) as executor:
        futures = [executor.submit(runOne, workItem) for workItem in workItems]

        #Everything is printed from here, on the main thread. Concurrently the workers
        #only ever append to their own buffer, so no output can interleave.
        for future in as_completed(futures):
            plan, index, testCase = future.result()
            completedCases += 1

            if(not liveOutput):
                bufferedOutput = testCase.flushOutput()
                if(bufferedOutput):
                    print(bufferedOutput)

            durationMs = plan.testCaseResults[index].get("durationMs", 0.0)
            print("[%i/%i] %s (%s) - %.3fms" % (completedCases, totalCases, testCase.getTestCaseName(), plan.testPlanName, durationMs))
