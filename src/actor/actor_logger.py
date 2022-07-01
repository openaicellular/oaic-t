# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

import logging

logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    handlers=[
                        logging.FileHandler("server_log_debug.log"),
                        logging.StreamHandler()
                    ]
                    )
logger = logging.getLogger('OAIC-T Actor')
