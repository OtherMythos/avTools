import xml.etree.cElementTree as ET

class JUnitFileWriter:
    def __init__(self):
        pass

    def buildMessage(self, failureMessageLines):
        #A failure message opens with a "Test Case <name>" title and a separator line, neither of
        #which say anything the testcase element doesn't already. Dropping them is only safe when
        #they're actually there - a message built by the runner itself can be a single line.
        lines = [l.rstrip("\n") for l in failureMessageLines]
        if(len(lines) > 2 and lines[1].startswith("===")):
            lines = lines[2:]

        return "\n".join(lines[:6])

    def write(self, results, outPath):
        print("Writing results to %s" % outPath)

        root = ET.Element("testsuites")
        for testProject in results:
            for testPlan in testProject:
                plan = ET.SubElement(root, "testsuite")
                plan.set("name", testPlan["testPlanName"])
                for y in testPlan["results"]:
                    testCase = ET.SubElement(plan, "testcase")
                    testCase.set("name", y["testName"])
                    durationMs = y.get("durationMs")
                    if durationMs is not None:
                        testCase.set("time", "%.3f" % (durationMs / 1000.0))
                    if y["failure"]:
                        failureEntry = ET.SubElement(testCase, "failure")
                        failureEntry.set("message", self.buildMessage(y["failureMessage"]))
                        failureEntry.set("type", "EngineCrash" if y.get("engineCrashed") else "AssertionError")

        tree = ET.ElementTree(root)
        ET.indent(tree, space="    ", level=0)
        tree.write(outPath, encoding='utf-8', xml_declaration=True)
