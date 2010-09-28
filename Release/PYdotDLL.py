# coding: utf-8

import os
import sys
import re
import ctypes
import traceback


PYdotDLL_GLOBAL = {} # PYdotDLL global data dictionary, all global data which is used by pydotdll is stored here

def PYdotDLL_UTILS_InlineHook(where, fake):
    if type(where) is str:
        dllname, procname = where.split('.')
        hdll = ctypes.windll.kernel32.LoadLibraryA(dllname)
        where = ctypes.windll.kernel32.GetProcAddress(hdll, procname)
    if type(where) is int:
        #origin = ctypes.c_long()
        #ctypes.cdll.PYdotDLL.InlineHook(where, fake, ctypes.byref(origin))
        #return origin.value
        return ctypes.cdll.PYdotDLL.InlineHook(where, fake)
    return 0

def PYdotDLL_HOOK_ReturnOriginFunction(*args):
    invoker = traceback.extract_stack()[-2][2]
    global PYdotDLL_GLOBAL
    return PYdotDLL_GLOBAL['hook'][invoker][0](*args)

def PYdotDLL_HOOK_Decorator(where, functype=ctypes.WINFUNCTYPE, **kw):
    def _hook(f):
        fargs = f.func_code.co_varnames[:f.func_code.co_argcount]
        gettype = lambda x: kw.get(x, ctypes.c_ulong)
        ftype = functype(gettype('restype'), *tuple([gettype(x) for x in fargs]))
        fake = ftype(f)
        origin = PYdotDLL_UTILS_InlineHook(where, fake)
        if origin:
            origin = ftype(origin)
        global PYdotDLL_GLOBAL
        if not PYdotDLL_GLOBAL.has_key('hook'):
            PYdotDLL_GLOBAL['hook'] = {}
        PYdotDLL_GLOBAL['hook'][f.__name__] = [origin,fake]

        def AKUMA(*args, **kw):
            print 'Go home, akuma will eat you. hahaaa !!'
        return AKUMA
    return _hook

HOOKDecorator = PYdotDLL_HOOK_Decorator
OriginFunction = PYdotDLL_HOOK_ReturnOriginFunction

# Todo:
if __name__ == '__m123ain__':
    print 'ooh! here is not entry.'
else:

    # 
    __file__ = traceback.extract_stack()[1][0]
    sys.path.insert(0,os.path.dirname(__file__))
    
    #hdll = ctypes.windll.kernel32.LoadLibraryA("user32")
    #where = ctypes.windll.kernel32.GetProcAddress(hdll, "MessageBoxW")
    #ctypes.cdll.PYdotDLL.EatHook(hdll, where, 0)
    #where = ctypes.windll.kernel32.GetProcAddress(hdll, "MessageBoxW")
    
    # Ensure and Open Console
    ctypes.windll.kernel32.AllocConsole()
    sys.stderr = sys.stdout = open("CONOUT$", "w")
    sys.stdin = open('CONIN$', 'r')
    print 'Test Console .'
    sys.stdout.flush()

    @HOOKDecorator('user32.MessageBoxA', title=ctypes.c_char_p)
    def MessageBoxA(handle, msg, title, type):
        return OriginFunction(handle, msg, 'PYdotDLL!!', type)

    @HOOKDecorator('kernel32.LoadLibraryA', dll=ctypes.c_char_p)
    def LoadLibraryA(dll):
        handle = OriginFunction(dll)
        print '%s: 0x%08X' % (os.path.basename(dll), handle)
        return handle

    @HOOKDecorator('wininet.InternetConnectA', servername=ctypes.c_char_p)
    def InternetConnectA(handle, servername, serverport, username, password, service, flags, context):
        if servername.lower() == 'www.baidu.com':
            servername = 'bbs.pediy.com'
            print 'Redirect It ! : www.baidu.com -> bbs.pediy.com'
            sys.stdout.flush()
        return OriginFunction(handle, servername, serverport, username, password, service, flags, context)
