MINUTE = 60


class Config(object):
    forward_scan_blocks = 512
    back_scan_blocks = 512

    forward_scan_seconds = 120 * MINUTE
    back_scan_seconds = 120 * MINUTE
