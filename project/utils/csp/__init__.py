import os


if os.name == "nt":
    from project.utils.csp.win_csp import WinCspManager
    csp_manager = WinCspManager()
else:
    from project.utils.csp.linux_csp import LinCspManager
    csp_manager = LinCspManager()
