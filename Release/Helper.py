# coding:utf-8

import sys
import ctypes
import getopt

PAGE_READWRITE = 0x04
PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)
VIRTUAL_MEM = (0x1000 | 0x2000)
SystemHandleInformation = 16
FileNameInformation = 9

Ntdll = ctypes.windll.ntdll
Kernel32 = ctypes.windll.Kernel32
Usre32 = ctypes.windll.User32

def InjectDLL(dll, PID):
    dllLen = len(dll)
    hProcs = Kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, PID)
    argAddy = Kernel32.VirtualAllocEx(hProcs, 0, dllLen, VIRTUAL_MEM, PAGE_READWRITE)
    wrote = ctypes.c_int(0)
    kernel.WriteProcessMemory(hProcs, argAddy, dll, dllLen, ctypes.byref(wrote))
    hKernal = Kernel32.GetModuleHandleA("kernel32.dll")
    hLib = Kernel32.GetProcAddress(hKernel, "LoadLibraryA")
    t_Id = ctypes.c.ulong(0)
    Kernel32.CreateRemoteThread(hProcs, None, 0, hLib, argAddy, 0, ctypes.byref(t_Id))
    return t_Id

def QueryHandles():
    need = ctypes.c_long()
    buf = ctypes.create_string_buffer(1024)
    Ntdll.ZwQuerySystemInformation(SystemHandleInformation, buf, len(buf), ctypes.byref(need))
    buf = ctypes.create_string_buffer(need.value)
    Ntdll.ZwQuerySystemInformation(SystemHandleInformation, buf, len(buf), ctypes.byref(need))
    count = ctypes.cast(buf, ctypes.POINTER(ctypes.c_long)).contents.value
    return [ctypes.cast(buf[4+i*16+6:], ctypes.POINTER(ctypes.c_ushort)).contents.value for i in xrange(count)]



if __name__ == '__main__':
    for x in QueryHandles():
        print hex(x)