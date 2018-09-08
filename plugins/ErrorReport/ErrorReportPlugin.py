# Plugin to allow automatic error reporting in ZeroNet
# Usage example:
#   from ErrorReport import reportErrors
#   @reportErrors(classes=(IOError, AssertionError))
#   def someFunction():
#       ...

import inspect, sys, gevent
import ErrorReportFormat
global config

# - Functions that traverse the stack and extract informations -

def countspaces (line):
    return len(line) - len(line.lstrip(" "))

def outputFrame (tb_frame, short=False):
    glob, loc, code = tb_frame.f_globals, tb_frame.f_locals, tb_frame.f_code
    # Skip to next frame if we are in current file and package
    if glob["__name__"] == "ErrorReport" and glob["__file__"] == __file__:
        return None
    source, fstartln = [], 0
    try:
        source, fstartln = inspect.getsourcelines(code)
    except Exception as e:
        pass
    sourcecode = [(linenumber + fstartln, linecontent.rstrip("\n")) for linenumber, linecontent in enumerate(source)]
    shortcontext = None
    for linenumber, linecontent in enumerate(source):
        if linenumber + fstartln == tb_frame.f_lineno:
            shortcontext = linecontent.rstrip("\n")
    # For global if __name__ == '__main__' the above does not work        
    if shortcontext is None:
        try:
            module = inspect.getmodule(code)
            with open(module.__file__, 'r') as modfile:
                filecontent = modfile.read().split("\n")
            for linenumber, linecontent in enumerate(filecontent):
                if linenumber + 1 == tb_frame.f_lineno:
                    shortcontext = linecontent.rstrip("\n")
            sourcecode = []
            initialspaces = countspaces(shortcontext)
            curline = tb_frame.f_lineno - 1
            while True:
                sourcecode.append((curline + 1, filecontent[curline]))
                if countspaces(filecontent[curline]) < initialspaces:
                    break
                curline -= 1
                if curline < 0:
                    break
            sourcecode.reverse()
            curline = tb_frame.f_lineno
            while True:
                if not filecontent[curline]:
                    break
                if countspaces(filecontent[curline]) >= initialspaces:
                    sourcecode.append((curline + 1, filecontent[curline]))
                curline += 1
        except Exception as e:
            pass
    if shortcontext is None:
        shortcontext = "<Source code not found>"
    localvars = tb_frame.f_locals
    globalvars = {key: value for key, value in tb_frame.f_globals.items() if not key.startswith("__") and not hasattr(value, "__call__") and not inspect.ismodule(value)}
    return { "package": glob["__name__"], "file": glob["__file__"], "function": code.co_name, "lineno": tb_frame.f_lineno, "shortcontext": shortcontext, "source": sourcecode, "localvars": localvars, "globalvars": globalvars }

def getExtraInformations ():
    extrainformations = {
        "zeronet-version": config.version,
        "zeronet-revision": config.rev,
        "python-version": sys.version,
        "gevent-version": gevent.__version__
    }
    return extrainformations

def reportErrors (classes=(AssertionError,), formatting=formatTraceAsText):
    def decorator (f):
        def decorated (*args, **kwargs):
            try:
                f(*args, **kwargs)
            except classes as e:
                type, value, tb = sys.exc_info()
                erepr = str(e) if len(e.args) <= 1 else repr(e.args)
                exception = { "class": e.__class__.__name__, "value": erepr }
                detailedtrace = []
                if tb.tb_frame.f_back:
                    tbframe = tb.tb_frame.f_back
                    while True:
                        detailedtrace.append(outputFrame(tbframe))
                        if not tbframe.f_back:
                            break
                        tbframe = tbframe.f_back
                detailedtrace.reverse()
                while tb.tb_next:
                    detailedtrace.append(outputFrame(tb.tb_frame))
                    tb = tb.tb_next
                extrainfo = getExtraInformations()
                formatting(exception, detailedtrace, extrainfo)
        return decorated
    return decorator
