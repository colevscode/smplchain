# smplchain

Speed up and pitch up parts of a wav file using ffmpeg via pydub.

## Overview

`smplchain` is a simple sample chain tool that divides an audio file into N slices and applies different pitch/speed adjustments to each slice using the "chipmunk effect" (asetrate method). This tool is intended to be used while prepping a "sample chain" for playback in Shield Tracker. 

## Installation

This project uses Poetry for dependency management. Make sure you have Python ≥3.11 and Poetry installed.

```bash
poetry install
```

## Usage

```bash
poetry run python smplchain.py <input.wav> <semitone1> <semitone2> ... [options]
```

### Arguments

- `input.wav` - Input WAV file
- `semitone1 semitone2 ...` - Pitch adjustments in semitones for each slice
- `-o, --output` - Output WAV file (default: `output.wav`)
- `-N, --normalize` - Normalize output to -1 dBFS

**Important:** The number of semitone values you provide determines how many slices your audio will be divided into. Each slice gets the corresponding pitch adjustment.

- **3 values** = 3 equal slices
- **8 values** = 8 equal slices
- etc.


## Using smplchain

### How to create a sample chain

A sample chain is a single tone (such as a piano key being struck) recorded multiple times at different octaves in the same sample. This multi-octave sample can then be played by a sampler without significantly time-compressing the audio as the pitch increases by selecting the correct "slice" to play depending on the pitch. (Normally increasing the pitch by one octave would also double the speed of playback, reducing playback time by half.)

The steps towards creating a sample chain are:

1. First record a sequence of tones (typically C notes) increasing by 1 octave each. You can use one of the example midi files with ableton to create such a sample. (created with [txt2mid](https://github.com/alambicbicephale/txt2mid))
2. Pitch up any notes below the "reference" note (typically middle C) by the number of octaves below that reference. Also pitch down any notes above the reference. This will result in a sequence of notes with identical pitch, but different durations. 
3. In the sequencer for each note, select the correct slice in the sample based the note's octave, and pitch the sample up or down to match the note. In Shield Tracker these happen simultaneously. 

For example, in Shield Tracker, triggering a sample with a transpose value of "C5" will play the sample at it's original speed. Playing a C6 will both pitch up and speed up the sample. So we should selected slice in the sample chain that's stretched out to twice as long, and pitched down to C5. This will give us back the original C6 pitch at the correct speed.

## Example: 5-Octave Sample Chain

Convert an 8-slice chain where the first 5 slices span 5 octaves, and the last 3 are empty:

```bash
poetry run python smplchain.py talpha-standalone-5oct.wav 48 24 12 0 -12 0 0 0 -N -o talpha-5oct-stretched.wav
```

This creates:
- **slice 1:** +48 semitones (4 octaves up)
- **slice 2:** +24 semitones (2 octaves up)  
- **slice 3:** +12 semitones (1 octave up)
- **slice 4:** 0 semitones (unchanged)
- **slice 5:** -12 semitones (1 octave down)
- **slices 6-8:** 0 semitones (unchanged)
- **Normalized** to -1 dBFS

## Technical Details

- Uses FFmpeg's `asetrate` filter for pitch shifting (chipmunk effect)
- Maintains original duration by resampling back to original sample rate
- Each slice is padded or truncated to match original slice length
- Temporary files are automatically cleaned up

## Requirements

- Python ≥3.11
- FFmpeg (must be installed and available in PATH)
- pydub (installed via Poetry)

## Audio Format Support

Input files are processed through pydub, which supports many formats via FFmpeg. Output is always WAV format. 