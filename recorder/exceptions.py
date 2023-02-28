class UploadError(Exception):
    """Raised when an upload fails"""
    pass


class SpankbangUploadError(UploadError):
    """Raised when an upload fails"""
    pass


class YoutubeUploadError(UploadError):
    """Raised when an upload fails"""
    pass


class TelegramUploadError(UploadError):
    """Raised when an upload fails"""
    pass
