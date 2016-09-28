MINUTE = 60


CHAINS = {
    # local test chain.
    '0x158e9d2f6f3082a1168619e1d59e789e210bb17c9bf9e39041e42b922753a2f9': {
        'contracts': {
            'recorder': '0x199a239ec2f7c788ce324d28be96fab34f3577f7',
            'tracker': '0x30d0fa1219eb741a96b4d3c1bfb6080e45b6e5f6',
            'factory': '0x3e936836a40b1775c02e80409aba07109cf78d5e',
            'block_scheduler': '0xb6b5e12e7db3ed8af10ca273a88c991a1ed3e177',
            'timestamp_scheduler': '0x68e3669cad1bd372f44161992a5ab13be281cb80',
        },
    },
}


class Config(object):
    forward_scan_blocks = 512
    back_scan_blocks = 512

    forward_scan_seconds = 120 * MINUTE
    back_scan_seconds = 120 * MINUTE
