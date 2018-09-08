# - Formatting functions -

# The formats of the arguments are:
# exception: has "class" and "value"
# detailedtrace: is a list of frames (where None means the exception was trapped there)
#     package: The name of the package / module of the line
#     file: The name of the file
#     function: The name of the function
#     lineno: The number of line of the execution
#     shortcontext: The line corresponding to lineno
#     source: List of couples (linenumber, linecontent) of the source of the function
#     localvars: Function localvariables dictionary
#     globalvars: Function globalvariables dictionary, without functions and modules
# extrainformations: A dictionary with other available informations
def formatTraceAsText (exception, detailedtrace, extrainformations={}):
    print("*** EXCEPTION REPORT ***")
    print("%s: %s" % (exception["class"], exception["value"]))
    print("")
    if extrainformations:
        print("--- EXTRA INFORMATIONS")
        for key, value in extrainformations.items():
            print("%s: %s" % (key, value))
    print("--- SHORT REPORT")
    for frame in detailedtrace:
        if frame is None:
            print("Exception was trapped at")
        else:
            print("%s:%s#%s:%d - %s" % (frame["package"], frame["file"], frame["function"], frame["lineno"], frame["shortcontext"].lstrip(" ")))
    print("")
    print("--- FULL REPORT")
    for frame in detailedtrace:
        if frame is None:
            print("Exception was trapped here")
        else:
            print("At %s:%s#%s:%d" % (frame["package"], frame["file"], frame["function"], frame["lineno"]))
            print("%s" % "\n".join(["%8d %s" % (linenumber, linecontent) for linenumber, linecontent in frame["source"]]))
            if frame["localvars"]:
                print("Local variables:")
                for key, value in frame["localvars"].items():
                    print("    %s: %s" % (key, repr(value)))
            if frame["globalvars"]:
                print("Global variables:")
                for key, value in frame["globalvars"].items():
                    print("    %s: %s" % (key, repr(value)))
            print("")
    print("*** END OF REPORT ***")
            
