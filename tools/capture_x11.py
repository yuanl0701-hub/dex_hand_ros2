#!/usr/bin/env python3
"""Capture an X11 root window without external screenshot utilities."""

from __future__ import annotations

import argparse
import ctypes
from pathlib import Path

from PIL import Image


class XImage(ctypes.Structure):
    """Leading public fields of the Xlib XImage structure."""

    _fields_ = [
        ("width", ctypes.c_int),
        ("height", ctypes.c_int),
        ("xoffset", ctypes.c_int),
        ("format", ctypes.c_int),
        ("data", ctypes.c_void_p),
        ("byte_order", ctypes.c_int),
        ("bitmap_unit", ctypes.c_int),
        ("bitmap_bit_order", ctypes.c_int),
        ("bitmap_pad", ctypes.c_int),
        ("depth", ctypes.c_int),
        ("bytes_per_line", ctypes.c_int),
        ("bits_per_pixel", ctypes.c_int),
        ("red_mask", ctypes.c_ulong),
        ("green_mask", ctypes.c_ulong),
        ("blue_mask", ctypes.c_ulong),
    ]


def capture(display_name: str, width: int, height: int, output: Path) -> None:
    xlib = ctypes.CDLL("libX11.so.6")
    xlib.XOpenDisplay.argtypes = [ctypes.c_char_p]
    xlib.XOpenDisplay.restype = ctypes.c_void_p
    xlib.XDefaultScreen.argtypes = [ctypes.c_void_p]
    xlib.XDefaultScreen.restype = ctypes.c_int
    xlib.XRootWindow.argtypes = [ctypes.c_void_p, ctypes.c_int]
    xlib.XRootWindow.restype = ctypes.c_ulong
    xlib.XGetImage.argtypes = [
        ctypes.c_void_p,
        ctypes.c_ulong,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_uint,
        ctypes.c_uint,
        ctypes.c_ulong,
        ctypes.c_int,
    ]
    xlib.XGetImage.restype = ctypes.POINTER(XImage)
    xlib.XDestroyImage.argtypes = [ctypes.POINTER(XImage)]
    xlib.XCloseDisplay.argtypes = [ctypes.c_void_p]

    display = xlib.XOpenDisplay(display_name.encode())
    if not display:
        raise RuntimeError(f"unable to open X display {display_name}")
    image_pointer = None
    try:
        screen = xlib.XDefaultScreen(display)
        root = xlib.XRootWindow(display, screen)
        image_pointer = xlib.XGetImage(
            display,
            root,
            0,
            0,
            width,
            height,
            ctypes.c_ulong(-1).value,
            2,  # ZPixmap
        )
        if not image_pointer:
            raise RuntimeError("XGetImage failed")
        image = image_pointer.contents
        if image.bits_per_pixel != 32 or image.byte_order != 0:
            raise RuntimeError(
                f"unsupported XImage format: {image.bits_per_pixel} bpp, "
                f"byte_order={image.byte_order}"
            )
        size = image.bytes_per_line * image.height
        pixels = ctypes.string_at(image.data, size)
        screenshot = Image.frombytes(
            "RGB",
            (image.width, image.height),
            pixels,
            "raw",
            "BGRX",
            image.bytes_per_line,
            1,
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        screenshot.save(output)
    finally:
        if image_pointer:
            xlib.XDestroyImage(image_pointer)
        xlib.XCloseDisplay(display)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--display", default=":1")
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--height", type=int, default=1000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    capture(args.display, args.width, args.height, args.output)


if __name__ == "__main__":
    main()
