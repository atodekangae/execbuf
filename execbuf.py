#!/usr/bin/env python3

import sys
import ctypes
__all__ = ('create_executable_buffer', 'make_memory_executable')

if sys.platform == 'win32':
    LPVOID  = ctypes.c_void_p
    HANDLE  = LPVOID
    SIZE_T  = ctypes.c_size_t
    DWORD   = ctypes.c_uint32
    LPDWORD = ctypes.POINTER(DWORD)
    PDWORD  = LPDWORD

    def error_if_zero(result, func, args):
        if not result:
            raise ctypes.WinError()
        return result

    PAGE_NOACCESS          = 0x01
    PAGE_READONLY          = 0x02
    PAGE_READWRITE         = 0x04
    PAGE_WRITECOPY         = 0x08
    PAGE_EXECUTE           = 0x10
    PAGE_EXECUTE_READ      = 0x20
    PAGE_EXECUTE_READWRITE = 0x40
    PAGE_EXECUTE_WRITECOPY = 0x80
    PAGE_GUARD             = 0x100
    PAGE_NOCACHE           = 0x200
    PAGE_WRITECOMBINE      = 0x400

    _VirtualProtect = ctypes.windll.kernel32.VirtualProtect
    _VirtualProtect.argtypes = [LPVOID, SIZE_T, DWORD, PDWORD]
    _VirtualProtect.restype  = bool
    _VirtualProtect.errcheck = error_if_zero
    flOldProtect = DWORD(0)
    def VirtualProtect(lpAddress, dwSize, flNewProtect):
        _VirtualProtect(lpAddress, dwSize, flNewProtect, ctypes.byref(flOldProtect))
        return flOldProtect.value

    def make_memory_executable(buffer):
        VirtualProtect(buffer, ctypes.sizeof(buffer), PAGE_EXECUTE_READWRITE)
elif sys.platform == 'linux':
    libc = ctypes.CDLL('libc.so.6')

    PAGESIZE = libc.getpagesize()
    PROT_NONE  = 0x0
    PROT_READ  = 0x1
    PROT_WRITE = 0x2
    PROT_EXEC  = 0x4

    mprotect = libc.mprotect
    mprotect.restype = ctypes.c_int
    mprotect.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]

    def make_memory_executable(buffer):
        orig = ctypes.addressof(buffer)
        addr = orig & (~(PAGESIZE-1)) # assumes the page size is a pow of 2
        size = ((orig+len(buffer)+PAGESIZE-1) & (~(PAGESIZE-1))) - addr
        ret = mprotect(addr, size, PROT_READ|PROT_WRITE|PROT_EXEC)
        if ret == -1:
            raise Exception('An error occured during mprotect')
else:
    pass
def create_executable_buffer(init, size=None):
    if isinstance(init, bytes) and size is None:
        size = len(init)
    buffer = ctypes.create_string_buffer(init, size)
    make_memory_executable(buffer)
    return buffer
