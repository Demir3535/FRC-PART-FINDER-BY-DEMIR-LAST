"""
Güncel satıcı bağlantıları ve fiyatları barındıran statik FRC parça veritabanı.

Notlar:
- Yalnızca AndyMark, REV Robotics, CTRE, WCP (West Coast Products) ve Deküp Robotics listelenir.
- Fiyatlar en son Mart 2024 stoklarına göre doğrulanmıştır; değişiklik olması hâlinde bu dosya güncellenmelidir.
"""

FRC_PARTS_DATABASE = {
    # ============ MOTORLAR ============
    'neo': [
        {'name': 'NEO Brushless Motor', 'vendor': 'REV Robotics', 'price': 50.00,
         'url': 'https://www.revrobotics.com/rev-21-1650/', 'inStock': True},
        {'name': 'NEO Brushless Motor', 'vendor': 'AndyMark', 'price': 56.00,
         'url': 'https://www.andymark.com/products/rev-neo-brushless-motor', 'inStock': True},
    ],
    'neo motor': 'neo',
    'neo brushless': 'neo',

    'neo 550': [
        {'name': 'NEO 550 Brushless Motor', 'vendor': 'REV Robotics', 'price': 30.00,
         'url': 'https://www.revrobotics.com/rev-21-1651/', 'inStock': True},
        {'name': 'NEO 550 Brushless Motor', 'vendor': 'AndyMark', 'price': 34.99,
         'url': 'https://www.andymark.com/products/neo-550-motor', 'inStock': True},
    ],

    'falcon 500': [
        {'name': 'Falcon 500 Brushless Motor', 'vendor': 'CTRE', 'price': 219.99,
         'url': 'https://store.ctr-electronics.com/falcon-500-powered-by-talon-fx/', 'inStock': True},
    ],
    'falcon': 'falcon 500',

    'kraken': [
        {'name': 'Kraken X60 Brushless Motor', 'vendor': 'WCP (West Coast Products)', 'price': 217.99,
         'url': 'https://wcproducts.com/products/kraken', 'inStock': True},
        {'name': 'Kraken X60 Brushless Motor', 'vendor': 'CTRE', 'price': 217.99,
         'url': 'https://store.ctr-electronics.com/kraken-x60/', 'inStock': True},
    ],
    'kraken x60': 'kraken',
    'kraken motor': 'kraken',

    'cim motor': [
        {'name': 'CIM Motor', 'vendor': 'AndyMark', 'price': 29.00,
         'url': 'https://www.andymark.com/products/2-5-in-cim-motor', 'inStock': True},
    ],
    'cim': 'cim motor',

    'minicim': [
        {'name': 'MiniCIM Motor', 'vendor': 'AndyMark', 'price': 29.99,
         'url': 'https://www.andymark.com/products/mini-cim-motor', 'inStock': True},
    ],

    # ============ MOTOR SÜRÜCÜLER ============
    'spark max': [
        {'name': 'SPARK MAX Motor Controller', 'vendor': 'REV Robotics', 'price': 100.00,
         'url': 'https://www.revrobotics.com/rev-11-2158/', 'inStock': True},
        {'name': 'SPARK MAX Motor Controller', 'vendor': 'AndyMark', 'price': 105.00,
         'url': 'https://www.andymark.com/products/spark-max-motor-controller', 'inStock': True},
    ],
    'sparkmax': 'spark max',

    'talon srx': [
        {'name': 'Talon SRX Motor Controller', 'vendor': 'CTRE', 'price': 89.99,
         'url': 'https://store.ctr-electronics.com/talon-srx/', 'inStock': True},
        {'name': 'Talon SRX Motor Controller', 'vendor': 'AndyMark', 'price': 95.00,
         'url': 'https://www.andymark.com/products/talon-srx', 'inStock': True},
    ],

    'victor spx': [
        {'name': 'Victor SPX Motor Controller', 'vendor': 'CTRE', 'price': 55.00,
         'url': 'https://store.ctr-electronics.com/victor-spx/', 'inStock': True},
    ],
    'victor spx motor controller': 'victor spx',

    'falcon': [
        {'name': 'Falcon Motor', 'vendor': 'CTRE', 'price': 219.99,
         'url': 'https://store.ctr-electronics.com/falcon-500-powered-by-talon-fx/', 'inStock': True},
    ],

    # ============ SENSÖRLER ============
    'navx': [
        {'name': 'navX2-MXP Navigation Sensor', 'vendor': 'AndyMark', 'price': 115.00,
         'url': 'https://www.andymark.com/products/navx2-mxp-robotics-navigation-sensor', 'inStock': True},
    ],
    'navx2': 'navx',
    'navx-micro': 'navx',

    'pigeon': [
        {'name': 'Pigeon 2.0 IMU', 'vendor': 'CTRE', 'price': 199.99,
         'url': 'https://store.ctr-electronics.com/pigeon-2/', 'inStock': True},
        {'name': 'Pigeon 2.0 IMU', 'vendor': 'AndyMark', 'price': 205.00,
         'url': 'https://www.andymark.com/products/pigeon-2-0', 'inStock': True},
    ],
    'pigeon imu': 'pigeon',
    'pigeon 2': 'pigeon',
    'pigeon 2.0': 'pigeon',

    'cancoder': [
        {'name': 'CANcoder Magnetic Encoder', 'vendor': 'CTRE', 'price': 60.00,
         'url': 'https://store.ctr-electronics.com/cancoder/', 'inStock': True},
        {'name': 'CANcoder Magnetic Encoder', 'vendor': 'AndyMark', 'price': 60.00,
         'url': 'https://www.andymark.com/products/ctre-cancoder', 'inStock': True},
    ],

    'through bore encoder': [
        {'name': 'REV Through Bore Encoder', 'vendor': 'REV Robotics', 'price': 29.99,
         'url': 'https://www.revrobotics.com/rev-11-1271/', 'inStock': True},
    ],
    'rev encoder': 'through bore encoder',

    'limelight': [
        {'name': 'Limelight 3 Vision Camera', 'vendor': 'AndyMark', 'price': 449.99,
         'url': 'https://www.andymark.com/products/limelight-3', 'inStock': True},
    ],

    # ============ PNÖMATİK ============
    'solenoid valve': [
        {'name': 'Single Acting Solenoid Valve', 'vendor': 'AndyMark', 'price': 19.99,
         'url': 'https://www.andymark.com/products/single-acting-solenoid-valve', 'inStock': True},
        {'name': 'Double Acting Solenoid Valve', 'vendor': 'AndyMark', 'price': 29.99,
         'url': 'https://www.andymark.com/products/double-acting-solenoid-valve', 'inStock': True},
    ],
    'solenoid': 'solenoid valve',

    'pneumatic cylinder': [
        {'name': 'Pneumatic Cylinder 1.5" Bore', 'vendor': 'AndyMark', 'price': 44.99,
         'url': 'https://www.andymark.com/products/pneumatic-cylinder', 'inStock': True},
        {'name': 'Pneumatic Cylinder 1.125" Bore', 'vendor': 'WCP (West Coast Products)', 'price': 52.99,
         'url': 'https://wcproducts.com/products/pneumatic-cylinder', 'inStock': True},
    ],
    'cylinder': 'pneumatic cylinder',

    'compressor': [
        {'name': 'VIAIR 90C Compressor', 'vendor': 'AndyMark', 'price': 49.99,
         'url': 'https://www.andymark.com/products/viair-90c-compressor', 'inStock': True},
    ],

    # ============ GÜÇ & ELEKTRONİK ============
    'pdh': [
        {'name': 'REV Power Distribution Hub', 'vendor': 'REV Robotics', 'price': 250.00,
         'url': 'https://www.revrobotics.com/rev-11-1850/', 'inStock': True},
        {'name': 'REV Power Distribution Hub', 'vendor': 'AndyMark', 'price': 255.00,
         'url': 'https://www.andymark.com/products/rev-power-distribution-hub', 'inStock': True},
    ],
    'power distribution hub': 'pdh',

    'battery': [
        {'name': 'MK ES17-12 12V SLA Battery (Set of 2)', 'vendor': 'AndyMark', 'price': 87.00,
         'url': 'https://andymark.com/products/mk-es17-12-12v-sla-battery-set-of-2', 'inStock': True},
    ],

    'roborio': [
        {'name': 'NI roboRIO 2.0', 'vendor': 'AndyMark', 'price': 499.99,
         'url': 'https://andymark.com/products/ni-roborio-2-0', 'inStock': True},
    ],
    'roborio 2': 'roborio',
    'roborio 2.0': 'roborio',

    'radio': [
        {'name': 'OpenMesh OM5P-AN Radio', 'vendor': 'AndyMark', 'price': 69.99,
         'url': 'https://www.andymark.com/products/openmesh-radio', 'inStock': True},
    ],

    # ============ AKTARMA ORGANLARI ============
    'colson wheel': [
        {'name': '6" Colson Wheel', 'vendor': 'AndyMark', 'price': 19.99,
         'url': 'https://andymark.com/products/sds-colson-wheel', 'inStock': True},
    ],

    'mecanum wheel': [
        {'name': '4" Mecanum Wheel Set', 'vendor': 'AndyMark', 'price': 199.99,
         'url': 'https://andymark.com/pages/search-results-page?q=mecanum%20wheel', 'inStock': True},
        {'name': '6" Mecanum Wheel Set', 'vendor': 'WCP (West Coast Products)', 'price': 249.99,
         'url': 'https://wcproducts.com/products/mecanum-wheels', 'inStock': True},
    ],

    'roller chain': [
        {'name': '#25 Roller Chain (10 ft)', 'vendor': 'AndyMark', 'price': 14.99,
         'url': 'https://andymark.com/products/single-strand-riveted-roller-chain-10?variant=44493452476588', 'inStock': True},
        {'name': '#25 Roller Chain (10 ft)', 'vendor': 'WCP (West Coast Products)', 'price': 18.99,
         'url': 'https://wcproducts.com/products/roller-chain', 'inStock': True},
    ],

    'timing belt': [
        {'name': 'HTD 5mm Timing Belt', 'vendor': 'AndyMark', 'price': 9.99,
         'url': 'https://www.andymark.com/products/timing-belt-htd-5mm', 'inStock': True},
        {'name': 'GT2 Timing Belt', 'vendor': 'WCP (West Coast Products)', 'price': 12.99,
         'url': 'https://wcproducts.com/products/gt2-timing-belts', 'inStock': True},
    ],

    'gearbox': [
        {'name': 'Toughbox Mini Gearbox', 'vendor': 'AndyMark', 'price': 89.99,
         'url': 'https://www.andymark.com/products/toughbox-mini', 'inStock': True},
        {'name': '3 CIM Ball Shifter', 'vendor': 'WCP (West Coast Products)', 'price': 249.99,
         'url': 'https://wcproducts.com/products/3-cim-ball-shifter', 'inStock': True},
    ],

    # ============ KONUSTRÜKSİYON ============
    'aluminum tube': [
        {'name': '1x1" Aluminum Tube', 'vendor': 'AndyMark', 'price': 19.99,
         'url': 'https://www.andymark.com/products/1-x-1-aluminum-tube', 'inStock': True},
        {'name': '2x1" Aluminum Tube', 'vendor': 'WCP (West Coast Products)', 'price': 24.99,
         'url': 'https://wcproducts.com/products/thunderhex-tube', 'inStock': True},
    ],
    'tube': 'aluminum tube',

    'hex bearing': [
        {'name': '1/2" Hex Bearing', 'vendor': 'AndyMark', 'price': 4.99,
         'url': 'https://www.andymark.com/products/1-2-hex-bearing', 'inStock': True},
        {'name': '1/2" Hex Bearing', 'vendor': 'WCP (West Coast Products)', 'price': 4.49,
         'url': 'https://wcproducts.com/products/hex-bearings', 'inStock': True},
    ],
    'bearing': 'hex bearing',

    # ============ YENİ MOTORLAR ============
    'neo vortex': [
        {'name': 'NEO Vortex Brushless Motor', 'vendor': 'REV Robotics', 'price': 90.00,
         'url': 'https://www.revrobotics.com/rev-21-1652/', 'inStock': True},
    ],
    'vortex': 'neo vortex',
    'vortex motor': 'neo vortex',

    'neverest': [
        {'name': 'NeveRest Motor', 'vendor': 'AndyMark', 'price': 12.80,
         'url': 'https://www.andymark.com/products/neverest-series-motor-only', 'inStock': True},
    ],
    'neverest motor': 'neverest',

    # ============ YENİ MOTOR KONTROLCÜLER ============
    'spark flex': [
        {'name': 'SPARK Flex Motor Controller', 'vendor': 'REV Robotics', 'price': 110.00,
         'url': 'https://www.revrobotics.com/rev-11-2159/', 'inStock': True},
    ],
    'sparkflex': 'spark flex',

    # ============ YENİ SENSÖRLER ============
    'through bore encoder': [
        {'name': 'REV Through Bore Encoder', 'vendor': 'REV Robotics', 'price': 48.00,
         'url': 'https://www.revrobotics.com/rev-11-1271/', 'inStock': True},
    ],
    'through bore': 'through bore encoder',
    'bore encoder': 'through bore encoder',

    'cancoder standard': [
        {'name': 'CANcoder Magnetic Encoder (Standard)', 'vendor': 'CTRE', 'price': 69.99,
         'url': 'https://store.ctr-electronics.com/cancoder/', 'inStock': True},
    ],

    'cancoder wired': [
        {'name': 'CANcoder Magnetic Encoder (Wired)', 'vendor': 'CTRE', 'price': 89.99,
         'url': 'https://store.ctr-electronics.com/cancoder/', 'inStock': True},
    ],

    # ============ SWERVE & DRIVE ============
    'swerve': [
        {'name': 'Swerve & Steer Module', 'vendor': 'AndyMark', 'price': 238.00,
         'url': 'https://www.andymark.com/products/swerve-and-steer', 'inStock': True},
    ],
    'swerve module': 'swerve',
    'swerve and steer': 'swerve',

    # ============ CHAIN & SPROCKETS ============
    'chain 25': [
        {'name': '#25 Roller Chain (10 ft)', 'vendor': 'WCP (West Coast Products)', 'price': 12.99,
         'url': 'https://wcproducts.com/collections/all', 'inStock': True},
    ],

    'chain 35': [
        {'name': '#35 Roller Chain (10 ft)', 'vendor': 'WCP (West Coast Products)', 'price': 12.99,
         'url': 'https://wcproducts.com/collections/all', 'inStock': True},
    ],

    'sprocket 25': [
        {'name': '#25 Sprockets', 'vendor': 'WCP (West Coast Products)', 'price': 11.99,
         'url': 'https://wcproducts.com/collections/all', 'inStock': True},
    ],

    'sprocket 35': [
        {'name': '#35 Sprockets', 'vendor': 'WCP (West Coast Products)', 'price': 15.99,
         'url': 'https://wcproducts.com/collections/all', 'inStock': True},
    ],

    # ============ REV ROBOTICS EK ÜRÜNLER ============
    'color sensor': [
        {'name': 'REV Color Sensor V3', 'vendor': 'REV Robotics', 'price': 30.00,
         'url': 'https://www.revrobotics.com/rev-31-1557/', 'inStock': True},
    ],
    'color sensor v3': 'color sensor',

    '2m distance sensor': [
        {'name': 'REV 2m Distance Sensor', 'vendor': 'REV Robotics', 'price': 40.00,
         'url': 'https://www.revrobotics.com/rev-31-1505/', 'inStock': True},
    ],
    'distance sensor': '2m distance sensor',

    'pneumatic hub': [
        {'name': 'REV Pneumatic Hub', 'vendor': 'REV Robotics', 'price': 175.00,
         'url': 'https://www.revrobotics.com/rev-11-1852/', 'inStock': True},
    ],

    'radio power module': [
        {'name': 'REV Radio Power Module', 'vendor': 'REV Robotics', 'price': 25.00,
         'url': 'https://www.revrobotics.com/rev-11-1856/', 'inStock': True},
    ],
    'rpm': 'radio power module',

    # ============ CTRE EK ÜRÜNLER ============
    'talon fx': [
        {'name': 'Talon FX Motor Controller', 'vendor': 'CTRE', 'price': 219.99,
         'url': 'https://store.ctr-electronics.com/falcon-500-powered-by-talon-fx/', 'inStock': True},
    ],

    'mag encoder': [
        {'name': 'Mag Encoder (Relative)', 'vendor': 'CTRE', 'price': 35.00,
         'url': 'https://store.ctr-electronics.com/mag-encoder-relative/', 'inStock': True},
    ],

    # ============ ANDYMARK EK MOTORLAR ============
    'bag motor': [
        {'name': 'BAG Motor', 'vendor': 'AndyMark', 'price': 24.00,
         'url': 'https://www.andymark.com/products/bag-motor', 'inStock': True},
    ],
    'bag': 'bag motor',

    '775pro': [
        {'name': '775pro Motor', 'vendor': 'AndyMark', 'price': 18.00,
         'url': 'https://www.andymark.com/products/775pro-motor', 'inStock': True},
    ],
    '775 pro': '775pro',
    'redline': '775pro',

    # ============ ANDYMARK WHEELS ============
    'hi-grip wheel': [
        {'name': '6" Hi-Grip Wheel', 'vendor': 'AndyMark', 'price': 15.99,
         'url': 'https://www.andymark.com/products/6-in-hi-grip-wheel', 'inStock': True},
    ],
    'hi grip': 'hi-grip wheel',
    'higrip': 'hi-grip wheel',

    # ============ ANDYMARK VISION ============
    'limelight 3': [
        {'name': 'Limelight 3 Vision Camera', 'vendor': 'AndyMark', 'price': 449.99,
         'url': 'https://www.andymark.com/products/limelight-3', 'inStock': True},
    ],
    'limelight3': 'limelight 3',
}


VENDOR_SEARCH_URLS = {
    'AndyMark': 'https://www.andymark.com/search?q=',
    'REV Robotics': 'https://www.revrobotics.com/search/?q=',
    'CTRE': 'https://store.ctr-electronics.com/search?q=',
    'WCP (West Coast Products)': 'https://wcproducts.com/search?q=',
    'Deküp Robotics': 'https://www.dekuprobotics.com/search?q=',
}
