"""Generate application icons (PNG and ICO) for GharBeka release packaging.

Creates a sleek modern desktop icon with a tilted monitor and rotation badge.
"""

from pathlib import Path
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (
    QImage,
    QPainter,
    QColor,
    QLinearGradient,
    QPainterPath,
    QPen,
    QBrush,
    QFont,
)
from PySide6.QtWidgets import QApplication
import sys


def generate_icon(size: int = 256) -> QImage:
    image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)

    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    s = float(size)
    margin = s * 0.05
    rect = QRectF(margin, margin, s - 2 * margin, s - 2 * margin)

    # 1. Background Rounded Tile with subtle violet gradient
    bg_path = QPainterPath()
    bg_path.addRoundedRect(rect, s * 0.22, s * 0.22)

    grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
    grad.setColorAt(0.0, QColor("#1e1b4b"))  # Deep Indigo
    grad.setColorAt(0.5, QColor("#0f172a"))  # Slate Dark
    grad.setColorAt(1.0, QColor("#090d16"))  # Dark Charcoal

    painter.fillPath(bg_path, grad)

    # Glowing subtle border
    border_pen = QPen(QColor("#8b5cf6"), s * 0.02)
    painter.strokePath(bg_path, border_pen)

    # 2. Tilted monitor frame in center
    painter.save()
    center_x = s * 0.5
    center_y = s * 0.48
    painter.translate(center_x, center_y)
    painter.rotate(18.0)  # Playfully tilted 18 degrees

    # Monitor bezel
    mon_w = s * 0.52
    mon_h = s * 0.36
    mon_rect = QRectF(-mon_w / 2, -mon_h / 2, mon_w, mon_h)

    # Outer screen frame
    bezel_path = QPainterPath()
    bezel_path.addRoundedRect(mon_rect, s * 0.03, s * 0.03)
    painter.fillPath(bezel_path, QColor("#161b2e"))
    painter.strokePath(bezel_path, QPen(QColor("#38bdf8"), s * 0.02))

    # Inner display glow
    inner_margin = s * 0.025
    inner_rect = QRectF(
        -mon_w / 2 + inner_margin,
        -mon_h / 2 + inner_margin,
        mon_w - 2 * inner_margin,
        mon_h - 2 * inner_margin,
    )
    inner_path = QPainterPath()
    inner_path.addRoundedRect(inner_rect, s * 0.015, s * 0.015)
    inner_grad = QLinearGradient(inner_rect.topLeft(), inner_rect.bottomRight())
    inner_grad.setColorAt(0.0, QColor("#8b5cf6"))
    inner_grad.setColorAt(1.0, QColor("#38bdf8"))
    painter.fillPath(inner_path, inner_grad)

    # Monitor stand neck & base
    painter.restore()

    # Stand neck
    neck_w = s * 0.08
    neck_h = s * 0.14
    neck_rect = QRectF(center_x - neck_w / 2, center_y + s * 0.2, neck_w, neck_h)
    painter.fillRect(neck_rect, QColor("#334155"))

    # Stand base
    base_w = s * 0.32
    base_h = s * 0.045
    base_rect = QRectF(center_x - base_w / 2, center_y + s * 0.32, base_w, base_h)
    base_path = QPainterPath()
    base_path.addRoundedRect(base_rect, base_h / 2, base_h / 2)
    painter.fillPath(base_path, QColor("#475569"))
    painter.strokePath(base_path, QPen(QColor("#0ea5e9"), s * 0.01))

    # Circular rotation badge in bottom-right
    badge_r = s * 0.16
    badge_center = QPointF(s * 0.78, s * 0.78)
    badge_rect = QRectF(badge_center.x() - badge_r, badge_center.y() - badge_r, badge_r * 2, badge_r * 2)

    badge_grad = QLinearGradient(badge_rect.topLeft(), badge_rect.bottomRight())
    badge_grad.setColorAt(0.0, QColor("#f59e0b"))
    badge_grad.setColorAt(1.0, QColor("#ef4444"))
    painter.setBrush(QBrush(badge_grad))
    painter.setPen(QPen(QColor("#ffffff"), s * 0.015))
    painter.drawEllipse(badge_rect)

    # 90° text on badge
    font = QFont("Segoe UI", int(s * 0.1), QFont.Weight.Bold)
    painter.setFont(font)
    painter.setPen(QPen(QColor("#ffffff")))
    painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, "90°")

    painter.end()
    return image


def create_ico_file(png_images: list[QImage], output_ico_path: Path) -> None:
    """Save multiple resolutions into a single Windows .ico binary."""
    # Build a standard Windows ICO file from PNG payloads
    # Header: 2 bytes reserved (0), 2 bytes type (1 for ico), 2 bytes count
    import io
    from PySide6.QtCore import QByteArray, QBuffer, QIODevice

    images_data = []
    for img in png_images:
        ba = QByteArray()
        buf = QBuffer(ba)
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        img.save(buf, "PNG")
        buf.close()
        images_data.append((img.width(), img.height(), bytes(ba)))

    # ICO directory header
    header = io.BytesIO()
    header.write(int(0).to_bytes(2, "little"))  # Reserved
    header.write(int(1).to_bytes(2, "little"))  # Type: 1 = ICO
    header.write(len(images_data).to_bytes(2, "little"))  # Count

    offset = 6 + 16 * len(images_data)
    entries = io.BytesIO()
    image_bodies = io.BytesIO()

    for width, height, data in images_data:
        w_byte = 0 if width >= 256 else width
        h_byte = 0 if height >= 256 else height
        entries.write(w_byte.to_bytes(1, "little"))
        entries.write(h_byte.to_bytes(1, "little"))
        entries.write(int(0).to_bytes(1, "little"))  # Colors in palette
        entries.write(int(0).to_bytes(1, "little"))  # Reserved
        entries.write(int(1).to_bytes(2, "little"))  # Color planes
        entries.write(int(32).to_bytes(2, "little"))  # Bits per pixel
        entries.write(len(data).to_bytes(4, "little"))  # Size of image data
        entries.write(offset.to_bytes(4, "little"))  # Offset of image data
        image_bodies.write(data)
        offset += len(data)

    output_ico_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_ico_path, "wb") as f:
        f.write(header.getvalue())
        f.write(entries.getvalue())
        f.write(image_bodies.getvalue())


def main():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    assets_dir = Path(__file__).resolve().parent.parent / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Generate 256x256 master PNG
    master_image = generate_icon(256)
    png_path = assets_dir / "icon.png"
    master_image.save(str(png_path), "PNG")
    print(f"Generated PNG: {png_path}")

    # Generate multiple resolutions for ICO: 256, 128, 64, 48, 32, 16
    resolutions = [256, 128, 64, 48, 32, 16]
    images = [generate_icon(res) for res in resolutions]
    ico_path = assets_dir / "icon.ico"
    create_ico_file(images, ico_path)
    print(f"Generated ICO: {ico_path}")


if __name__ == "__main__":
    main()
