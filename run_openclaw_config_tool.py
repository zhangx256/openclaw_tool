import sys
from pathlib import Path

_pkg_parent = str(Path(__file__).resolve().parent.parent)
if _pkg_parent not in sys.path:
    sys.path.insert(0, _pkg_parent)

from openclaw_tool.qt_import import import_qt
from openclaw_tool.ui.main_window import MainWindow


def main():
    _, _, QtWidgets = import_qt()
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    raise SystemExit(app.exec() if hasattr(app, "exec") else app.exec_())


if __name__ == "__main__":
    main()
