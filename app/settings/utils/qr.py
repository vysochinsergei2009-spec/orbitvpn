from io import BytesIO
import qrcode
from aiogram.types import BufferedInputFile


def generate_qr_file(
    data: str,
    filename: str = "qr_code.png",
) -> BufferedInputFile:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    bio = BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)

    return BufferedInputFile(bio.read(), filename=filename)
