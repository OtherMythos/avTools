import xml.etree.cElementTree as ET

class JUnitFileWriter:
    def __init__(self):
        pass

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
                    if y["failure"]:
                        failureEntry = ET.SubElement(testCase, "failure")
                        totalMessage = "\n".join(y["failureMessage"][2:8])
                        failureEntry.set("message", totalMessage)
                        failureEntry.set("type", "AssertionError")

        tree = ET.ElementTree(root)
        ET.indent(tree, space="    ", level=0)
        tree.write(outPath, encoding='utf-8', xml_declaration=True)
