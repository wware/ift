# Compute-efficient inverse Fourier transforms

It's pretty standard to build music synths out of voltage-controlled
oscillators, amplifiers, filters, etc. An alternative is to build sounds in the
frequency domain and play them using inverse Fourier transforms. The present
hack is an exploration of building large numbers of sine waves in a
compute-efficient manner for audio generation.

People sometimes talk about characterizing a sine wave using amplitude,
frequency, and phase. It turns out that frequency is really just a time
derivative of phase (give or take a factor of 2 pi) so we really only need
phase. The ear hears changes in phase but does not hear absolute phase.

![Silly diagram](https://raw.githubusercontent.com/wware/ift/plugh/sine_lookup_table.jpg)

    SAMPLE_RATE = 44100
    DT = 1. / SAMPLE_RATE
    # compute dPH and dA
    A = PH = 0              # loop over sinusoids
    for _ in xrange(SAMPLE_RATE):
        nextPH = PH + dPH
        nextA = A + dA
        X = A * sine_lookup(PH)
        # sum X over all sinusoids
        Y = sigmoid(X)      # avoid clipping
        # send Y to the DAC

I like the Teensy microcontroller for this kind of thing. I haven't used the
Teensy 4.0 yet but I have a couple of them waiting to be used. Teensys like
C++ code, so architecturally this should be written as C++ code, with SWIG
wrappers for running it on desktops/laptops from Python.

Near-term goal: Write a reference implementation in Python from which C++/asm
code for an ARM-based MCU could be easily written. Produce audio files on a
desktop and verify they sound right.

Longer-term goal: Wire up a DAC to a Teensy and run C/asm code on the Teensy.
Use an amp or earbuds to hear the result, it should sound like the reference
implementation.
