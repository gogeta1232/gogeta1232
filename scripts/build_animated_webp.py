"""Preserve the approved GIF frames and timing as lossless animated WebP."""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageSequence


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets/pixel-profile"
SOURCES = (
    "ember-studio-loop-v3",
    "ember-flame-v2",
    "robot-idle-v2",
    "pixel-divider-v4",
    "clapper-v2",
)


def digest(frame):
    # RGB values of fully transparent pixels have no visual meaning.
    background = Image.new("RGBA", frame.size)
    return hashlib.sha256(Image.alpha_composite(background, frame).tobytes()).hexdigest()


def build(name):
    with Image.open(ASSETS / f"{name}.gif") as source:
        loop = source.info.get("loop", 0)
        frames = []
        durations = []
        for frame in ImageSequence.Iterator(source):
            frames.append(frame.convert("RGBA"))
            durations.append(frame.info["duration"])
    target = ASSETS / f"{name}.webp"
    frames[0].save(
        target,
        format="WEBP",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=loop,
        lossless=True,
        # In lossless mode quality controls compression effort, not fidelity.
        quality=75,
        method=3,
    )
    decoded_durations = []
    with Image.open(target) as decoded:
        assert decoded.format == "WEBP" and decoded.n_frames == len(frames)
        assert decoded.info["loop"] == loop == 0
        for index, frame in enumerate(ImageSequence.Iterator(decoded)):
            rgba = frame.convert("RGBA")
            assert digest(rgba) == digest(frames[index]), (name, index)
            decoded_durations.append(frame.info["duration"])
    assert decoded_durations == durations, name
    return {
        "file": target.relative_to(ROOT).as_posix(),
        "source": f"assets/pixel-profile/{name}.gif",
        "frames": len(frames),
        "duration_ms": sum(durations),
        "bytes": target.stat().st_size,
        "lossless_frame_match": True,
        "timing_match": True,
        "infinite_loop": True,
    }


if __name__ == "__main__":
    report = [build(name) for name in SOURCES]
    (ASSETS / "animated-webp-qa.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
