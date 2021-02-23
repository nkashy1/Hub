"""
License:
This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import platform
import textwrap

import numpy as np

from .collections import dataset
from .collections.dataset.core import Transform
from .collections import tensor
from .collections.dataset import load as load_v0
from .collections.client_manager import init
import hub.config
from hub.api.dataset import Dataset
from hub.compute import transform
from hub.log import logger
import traceback
from hub.exceptions import DaskModuleNotInstalledException, HubDatasetNotFoundException

from bugout.app import Bugout

def local_mode():
    hub.config.HUB_REST_ENDPOINT = hub.config.HUB_LOCAL_REST_ENDPOINT


def dev_mode():
    hub.config.HUB_REST_ENDPOINT = hub.config.HUB_DEV_REST_ENDPOINT


def dtype(*args, **kwargs):
    return np.dtype(*args, **kwargs)


def load(tag):
    """
    Load a dataset from repository using given tag

    Args:
        tag: string
        using {username}/{dataset} format or file system, s3://, gcs://

    Notes
    ------
    It will try to load using old version and fall off on newer version

    """
    try:
        ds = load_v0(tag)
        logger.warning(
            "Deprecated Warning: Given dataset is using deprecated format v0.x. Please convert to v1.x version upon availability."
        )
        return ds
    except ImportError:
        raise DaskModuleNotInstalledException
    except HubDatasetNotFoundException:
        raise
    except Exception as e:
        pass
        # logger.warning(traceback.format_exc() + str(e))

    return Dataset(tag)

# Record import if user has opted in to analytics
from .config import BUGOUT_ACCESS_TOKEN, BUGOUT_JOURNAL_ID
reporter = Bugout(brood_api_url="https://auth.bugout.dev", spire_api_url="https://spire.bugout.dev")

platform_info = platform.uname()
report_os = platform_info.system
report_os_release = platform_info.release
report_machine = platform_info.machine
report_processor = platform_info.processor
report_python_version = platform.python_version()

content = textwrap.dedent(f"""
## System information
OS: `{report_os}` (release: {report_os_release})
Processor: `{report_machine}, {report_processor}`
Python: `{report_python_version}`

- - -

## User information
TODO: anonymized client ID from Hub config file
""")
reporter.create_entry(
    BUGOUT_ACCESS_TOKEN,
    BUGOUT_JOURNAL_ID,
    title=f"Hub import",
    content=content,
    tags=["import", f"os:{report_os}", f"python:{report_python_version}"],
)
