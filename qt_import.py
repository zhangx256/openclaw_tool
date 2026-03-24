def import_qt():
    try:
        from PyQt5 import QtCore, QtGui, QtWidgets  # type: ignore

        return QtCore, QtGui, QtWidgets
    except Exception:
        pass
    try:
        from PySide6 import QtCore, QtGui, QtWidgets  # type: ignore

        return QtCore, QtGui, QtWidgets
    except Exception as e:
        raise RuntimeError("Missing Qt bindings. Install PyQt5 or PySide6.") from e

