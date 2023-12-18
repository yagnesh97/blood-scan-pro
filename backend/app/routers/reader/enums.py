from enum import Enum


class MIMETypes(str, Enum):
    PDF = "application/pdf"
    JPEG = "image/jpeg"
    PNG = "image/png"

    @staticmethod
    def types() -> list[str]:
        """List of MIME types.

        Returns:
            list[str]: List of MIME types.
        """
        return list(map(lambda _: _.value, MIMETypes))
