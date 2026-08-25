from __future__ import annotations

from bot.services.uniquizer import AppliedOp

_TEMPLATES: dict[str, dict[str, str]] = {
    "ru": {
        "zoom_crop": "🔍 Масштаб и обрезка кадра на {percent}% — сбивает совпадение по границам кадра.",
        "micro_rotate": "🔄 Микроповорот кадра на {degrees}° — меняет геометрию видео для видеохэша.",
        "color_grade": "🎨 Цветокоррекция (гамма {gamma}, насыщенность {saturation}, контраст {contrast}) — меняет цветовой отпечаток.",
        "grain": "🌫 Добавлена лёгкая зернистость (сила {strength}) — меняет пиксельный хэш без потери качества на глаз.",
        "scanline": "📺 Добавлена едва заметная плывущая полоса — дополнительный визуальный шум для антидубликат-систем.",
        "border": "🖼 Добавлена микрорамка {px}px — меняет исходное разрешение и пропорции кадра.",
        "speed": "⏱ Скорость воспроизведения изменена на {factor}x — сдвигает длительность и покадровый отпечаток.",
        "pitch_shift": "🎧 Тон звука сдвинут на {semitones} полутона — меняет аудиоотпечаток.",
        "fade": "🔊 Добавлены плавные затухания звука в начале ({fade_in}с) и конце ({fade_out}с).",
        "metadata_reset": "🧹 Все метаданные файла удалены и пересозданы — новый хэш файла целиком.",
    },
    "en": {
        "zoom_crop": "🔍 Zoomed & cropped the frame by {percent}% — breaks frame-border matching.",
        "micro_rotate": "🔄 Micro-rotated the frame by {degrees}° — changes the video's geometric hash.",
        "color_grade": "🎨 Color-graded (gamma {gamma}, saturation {saturation}, contrast {contrast}) — changes the color fingerprint.",
        "grain": "🌫 Added subtle film grain (strength {strength}) — changes the pixel hash, invisible to the eye.",
        "scanline": "📺 Added a barely visible drifting scan line — extra visual noise against duplicate detectors.",
        "border": "🖼 Added a micro border ({px}px) — changes the original resolution and aspect.",
        "speed": "⏱ Playback speed changed to {factor}x — shifts duration and frame-by-frame fingerprint.",
        "pitch_shift": "🎧 Audio pitch shifted by {semitones} semitones — changes the audio fingerprint.",
        "fade": "🔊 Added smooth audio fade-in ({fade_in}s) and fade-out ({fade_out}s).",
        "metadata_reset": "🧹 All file metadata wiped and regenerated — a brand new file hash.",
    },
}


def explain(applied_ops: list[AppliedOp], lang: str) -> str:
    lang = lang if lang in _TEMPLATES else "ru"
    lines = []
    for op in applied_ops:
        template = _TEMPLATES[lang].get(op.key)
        if template is None:
            continue
        lines.append(template.format(**op.params))
    return "\n".join(lines)
