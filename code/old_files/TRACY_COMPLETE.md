# Tracy Profiler - Installation Complete! ✅

## What Was Done

1. ✅ **Tracy downloaded** to `/home/raj/Documents/Projects/system_software/tracy`
2. ✅ **Dependencies installed**: libglfw3, freetype, capstone, etc.
3. ✅ **Makefile updated** with Tracy support
4. ✅ **TracyClient.cpp created** in your project
5. ✅ **Test build successful** with Tracy enabled
6. ✅ **Documentation created**: `TRACY_SETUP.md` and `tracy_example.cpp`

## Quick Reference

### Build Commands

```bash
cd /home/raj/Documents/Projects/PCA/VLSI_across_wire/code

# Normal build (no profiling):
make clean && make

# Build with Tracy profiling:
make clean && make TRACY_ENABLED=1
```

### Adding Instrumentation

1. At top of `wireroute.cpp` after includes:
```cpp
#ifdef TRACY_ENABLE
#include "tracy/public/Tracy.hpp"
#endif
```

2. Wrap code sections:
```cpp
#ifdef TRACY_ENABLE
    ZoneScopedN("My Section Name");
#endif
// ... your code ...
```

### View Traces

- **Online**: https://tracy.nereid.pl/ (upload `.tracy` files)
- **Local**: Need to upgrade CMake to 3.25+ first

## Files Created

```
/home/raj/Documents/Projects/system_software/tracy/          # Tracy source
/home/raj/Documents/Projects/PCA/VLSI_across_wire/code/
    ├── TracyClient.cpp                                      # Tracy integration
    ├── tracy_example.cpp                                    # Examples
    ├── TRACY_SETUP.md                                       # Full guide
    ├── TRACY_COMPLETE.md                                    # This file
    └── Makefile                                             # Updated
```

## Next Steps

1. **Read** `TRACY_SETUP.md` for detailed instructions
2. **See examples** in `tracy_example.cpp`
3. **Add zones** to your parallel regions in `wireroute.cpp`
4. **Build** with `make TRACY_ENABLED=1`
5. **Run** your program to generate trace files
6. **Analyze** traces at https://tracy.nereid.pl/

## Common Issues

### "No such file or directory" when including Tracy
- Make sure you built with `TRACY_ENABLED=1`
- Check the include path in TracyClient.cpp

### No trace file generated
- Verify `TRACY_ENABLE` is defined (check compile command)
- Make sure you added Tracy zones to your code
- Run the program all the way to completion

### Build errors
- Run `make clean` first
- Check that Tracy directory exists: `ls /home/raj/Documents/Projects/system_software/tracy`

## For Your Assignment

Tracy will help you understand:
- **Load imbalance**: Which threads are idle when
- **Synchronization overhead**: Time spent in critical sections
- **Performance bottlenecks**: Where the time actually goes
- **Scalability issues**: Why performance drops at high thread counts

Use Tracy insights to answer the writeup questions about speedup limitations and performance drop-offs!

## Support

- Tracy documentation: https://github.com/wolfpld/tracy
- Tracy manual: https://github.com/wolfpld/tracy/releases (look for PDF)
- Your setup guide: `TRACY_SETUP.md`

---

**Installation Status**: ✅ COMPLETE  
**Build Test**: ✅ PASSED  
**Ready to Profile**: ✅ YES

Happy profiling! 🚀
