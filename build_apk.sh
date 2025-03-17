
#!/bin/bash

echo "Setting up buildozer environment..."
pip install buildozer
pip install cython

echo "Building APK..."
# Export Nix zlib paths to help buildozer find the dependencies
export ZLIB_ROOT=$(dirname $(dirname $(find /nix/store -name "libz.so" | grep -v gcc | head -1)))
export CFLAGS="-I$ZLIB_ROOT/include"
export LDFLAGS="-L$ZLIB_ROOT/lib"
export LD_LIBRARY_PATH="$ZLIB_ROOT/lib:$LD_LIBRARY_PATH"
export PKG_CONFIG_PATH="$ZLIB_ROOT/lib/pkgconfig:$PKG_CONFIG_PATH"

# Show environment for debugging
echo "Using zlib from: $ZLIB_ROOT"
echo "CFLAGS: $CFLAGS"
echo "LDFLAGS: $LDFLAGS"

# Run buildozer with verbose output
buildozer -v android debug

echo "Build complete. The APK should be in the ./bin directory."
