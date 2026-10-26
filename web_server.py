#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""本机网页入口。

在仓库根目录执行：

    python web_server.py

然后打开 http://127.0.0.1:8765/ 。桌面版仍使用 python main.py。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web.server import main


if __name__ == "__main__":
    sys.exit(main())
