# execbuf
This is a Python library for creating an executable buffer. Currently supports Windows and Linux. No extra dependencies required beside the standard library. Tested on Python 3.8.

## Why?
Executing machine code on a dynamically allocated memory region, which is prevented for normally allocated memory understandably for a security reason, is useful in some circumstances, most notably in JIT. However, there is no handy way to do that provided in Python. This library offers that capability.

## How
First, a buffer is created with `ctypes`' `create_string_buffer`. Subsequently, the buffer will have its attribute as to whether it is executable changed by an appropriate means depending on the platform on which the program is run. On Windows, modification of the attribute is achieved by invoking `VirtualProtect` with the argument of `PAGE_EXECUTE_READWRITE`. On Linux, it is realized by calling `mprotect` for the memory page the buffer belongs to with the argument of `PROT_READ|PROT_WRITE|PROT_EXEC`.

## Example
In conjunction with `ctypes`, you can use this library to create a function from machine code. The code below creates a function that returns the result of `rdtsc`.

```python
import ctypes
from execbuf import create_executable_buffer

code = ( # for x86-64
    b'\x0f\x31'         # rdtsc
    b'\x48\xc1\xe2\x20' # shl rdx, 32
    b'\x48\x09\xd0'     # or rax, rdx
    b'\xc3'             # ret
)
buf = create_executable_buffer(code)
rdtsc = ctypes.CFUNCTYPE(ctypes.c_uint64)(ctypes.addressof(buf))
# now rdtsc can be called just like any other functions
```

## Notes
* You have to retain a reference to a buffer created with `create_executable_buffer` as long as a function made of the buffer lives; otherwise Python's GC destroys the buffer before the function is destroyed, thereby making the function unusable.
* `ctypes.CFUNCTYPE` assumes a calling convention that varies with the platform. For example, in Windows' default calling convention the first argument is passed via `RCX`, whereas it is via `RDI` in the standard Linux ABI. This implies that even if we confine ourselves to a specific architecture, we would need an extra amount of work of copying registers to make a piece of machine code portable. In the example above, it was not necessary to address the issue as the created function had no parameters.
