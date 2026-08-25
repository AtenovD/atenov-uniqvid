from __future__ import annotations

import asyncio
import random
import uuid
from dataclasses import dataclass
from pathlib import Path

from bot.config import config


@dataclass
class AppliedOp:
    key: str
    params: dict[str, float | int | str]


@dataclass
class UniquizeResult:
    output_path: Path
    applied_ops: list[AppliedOp]


class FFmpegError(RuntimeError):
    pass


def _rand_sign() -> int:
    return random.choice((-1, 1))


def _op_zoom_crop(rng: random.Random) -> tuple[str, AppliedOp]:
    pct = round(rng.uniform(2.0, 5.0), 2)
    scale = 1 + pct / 100
    filt = f"scale=iw*{scale}:ih*{scale},crop=iw/{scale}:ih/{scale}"
    return filt, AppliedOp("zoom_crop", {"percent": pct})


def _op_micro_rotate(rng: random.Random) -> tuple[str, AppliedOp]:
    deg = round(rng.uniform(0.4, 1.2) * _rand_sign(), 2)
    rad = deg * 3.14159265 / 180
    filt = f"rotate={rad}:c=black@0,crop=iw*0.97:ih*0.97"
    return filt, AppliedOp("micro_rotate", {"degrees": deg})


def _op_color_grade(rng: random.Random) -> tuple[str, AppliedOp]:
    gamma = round(rng.uniform(0.95, 1.05), 3)
    saturation = round(rng.uniform(0.92, 1.08), 3)
    contrast = round(rng.uniform(0.95, 1.05), 3)
    filt = f"eq=gamma={gamma}:saturation={saturation}:contrast={contrast}"
    return filt, AppliedOp("color_grade", {"gamma": gamma, "saturation": saturation, "contrast": contrast})


def _op_grain(rng: random.Random) -> tuple[str, AppliedOp]:
    strength = rng.randint(4, 12)
    filt = f"noise=alls={strength}:allf=t"
    return filt, AppliedOp("grain", {"strength": strength})


def _op_scanline_mirror(rng: random.Random) -> tuple[str, AppliedOp]:
    # thin semi-transparent horizontal band drifting across the frame
    y_speed = round(rng.uniform(0.15, 0.35), 2)
    filt = (
        f"drawbox=x=0:y=ih*abs(sin(t*{y_speed}))-2:w=iw:h=2:color=white@0.05:t=fill"
    )
    return filt, AppliedOp("scanline", {"speed": y_speed})


def _op_border(rng: random.Random) -> tuple[str, AppliedOp]:
    px = rng.randint(2, 6)
    filt = f"pad=iw+{px * 2}:ih+{px * 2}:{px}:{px}:color=black@0.0"
    return filt, AppliedOp("border", {"px": px})


VIDEO_OPS = [_op_zoom_crop, _op_micro_rotate, _op_color_grade, _op_grain, _op_scanline_mirror, _op_border]


def _op_speed(rng: random.Random) -> tuple[float, AppliedOp]:
    speed = round(rng.uniform(0.97, 1.04), 3)
    return speed, AppliedOp("speed", {"factor": speed})


def _op_audio_pitch(rng: random.Random) -> tuple[str, AppliedOp]:
    semitone_shift = round(rng.uniform(-0.4, 0.4), 3)
    rate_mult = 2 ** (semitone_shift / 12)
    filt = f"asetrate=44100*{rate_mult},aresample=44100"
    return filt, AppliedOp("pitch_shift", {"semitones": semitone_shift})


def _op_fade(rng: random.Random, duration: float) -> tuple[str, AppliedOp]:
    fade_in = round(rng.uniform(0.2, 0.6), 2)
    fade_out = round(rng.uniform(0.2, 0.6), 2)
    fade_out_start = max(duration - fade_out, 0)
    filt = f"afade=t=in:st=0:d={fade_in},afade=t=out:st={fade_out_start}:d={fade_out}"
    return filt, AppliedOp("fade", {"fade_in": fade_in, "fade_out": fade_out})


async def _probe_duration(input_path: Path) -> float:
    proc = await asyncio.create_subprocess_exec(
        config.ffprobe_bin,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(input_path),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise FFmpegError(stderr.decode(errors="ignore"))
    try:
        return float(stdout.decode().strip())
    except ValueError:
        return 0.0


async def uniquize(input_path: Path, out_dir: Path, seed: int | None = None) -> UniquizeResult:
    rng = random.Random(seed)
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / f"uniq_{uuid.uuid4().hex}.mp4"

    duration = await _probe_duration(input_path)

    applied: list[AppliedOp] = []

    chosen_video_ops = rng.sample(VIDEO_OPS, k=rng.randint(4, len(VIDEO_OPS)))
    video_filters: list[str] = []
    for op in chosen_video_ops:
        filt, applied_op = op(rng)
        video_filters.append(filt)
        applied.append(applied_op)

    speed, speed_op = _op_speed(rng)
    video_filters.append(f"setpts={1 / speed}*PTS")
    applied.append(speed_op)

    audio_filters: list[str] = [f"atempo={speed}"]
    pitch_filt, pitch_op = _op_audio_pitch(rng)
    audio_filters.append(pitch_filt)
    applied.append(pitch_op)

    if duration > 1.5:
        fade_filt, fade_op = _op_fade(rng, duration / speed)
        audio_filters.append(fade_filt)
        applied.append(fade_op)

    vf = ",".join(video_filters)
    af = ",".join(audio_filters)

    new_uuid = str(uuid.uuid4())
    applied.append(AppliedOp("metadata_reset", {"uuid": new_uuid}))

    args = [
        config.ffmpeg_bin,
        "-y",
        "-i", str(input_path),
        "-vf", vf,
        "-af", af,
        "-map_metadata", "-1",
        "-metadata", f"comment={new_uuid}",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "160k",
        str(output_path),
    ]

    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0 or not output_path.exists():
        raise FFmpegError(stderr.decode(errors="ignore")[-2000:])

    return UniquizeResult(output_path=output_path, applied_ops=applied)
