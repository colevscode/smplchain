#!/usr/bin/env python
import argparse
from pydub import AudioSegment
import math
import tempfile
import subprocess
import os


def parse_args():
    parser = argparse.ArgumentParser(description="Divide a wav file into N parts and adjust pitch/speed of each part by semitones (chipmunk effect, asetrate method).")
    parser.add_argument("filename", type=str, help="Input .wav file")
    parser.add_argument("semitones", type=float, nargs='+', help="Pitch adjustments in semitones for each part (e.g. -12 0 12)")
    parser.add_argument("-o", "--output", type=str, default="output.wav", help="Output .wav file")
    parser.add_argument("-N", "--normalize", action="store_true", help="Normalize output to -1 dBFS")
    return parser.parse_args()


def semitones_to_speed(semitones):
    return 2 ** (semitones / 12)


def ffmpeg_asetrate(input_wav, output_wav, speed, orig_sr):
    new_sr = int(orig_sr * speed)
    filter_str = f"asetrate={new_sr},aresample={orig_sr}"
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", input_wav,
        "-filter:a", filter_str,
        output_wav
    ]
    subprocess.run(cmd, check=True)


def main():
    args = parse_args()
    audio = AudioSegment.from_file(args.filename)
    n_parts = len(args.semitones)
    part_len = len(audio) // n_parts
    out = AudioSegment.empty()
    orig_sr = audio.frame_rate
    for i, semitones in enumerate(args.semitones):
        start = i * part_len
        end = (i + 1) * part_len if i < n_parts - 1 else len(audio)
        part = audio[start:end]
        speed = semitones_to_speed(semitones)
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tf_in, \
             tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tf_out:
            part.export(tf_in.name, format="wav")
            ffmpeg_asetrate(tf_in.name, tf_out.name, speed, orig_sr)
            sped = AudioSegment.from_file(tf_out.name)
            # Pad or truncate to match original part length
            if len(sped) < len(part):
                padding = len(part) - len(sped)
                sped += AudioSegment.silent(duration=padding, frame_rate=orig_sr)
            elif len(sped) > len(part):
                sped = sped[:len(part)]
            out += sped
            os.unlink(tf_in.name)
            os.unlink(tf_out.name)
    if args.normalize:
        peak = out.max_dBFS
        target = -1.0
        gain = target - peak
        out = out.apply_gain(gain)
    out.export(args.output, format="wav")
    print(f"Wrote output to {args.output}")


if __name__ == "__main__":
    main() 