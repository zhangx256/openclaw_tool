from ..qt_import import import_qt
from ..app.plans import build_add_plan, build_custom_model_plan, build_delete_plan
from .runners import ModelTestRunner, Runner

_, _, QtWidgets = import_qt()


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenClaw 配置工具")
        self.setMinimumWidth(520)

        self.model_provider_edit = QtWidgets.QLineEdit()
        self.model_provider_edit.setPlaceholderText("可自定义，建议按照模型服务供应商填写")

        self.model_id_edit = QtWidgets.QLineEdit()
        self.model_id_edit.setPlaceholderText("模型ID，参考模型服务供应商API调用文档获取")

        self.model_base_url_edit = QtWidgets.QLineEdit()
        self.model_base_url_edit.setPlaceholderText("接口地址，参考模型服务供应商API调用文档获取")

        self.model_api_key_edit = QtWidgets.QLineEdit()
        self.model_api_key_edit.setPlaceholderText("密钥，参考模型服务供应商API调用文档获取")
        self.model_api_key_edit.setEchoMode(QtWidgets.QLineEdit.Password)

        self.model_test_btn = QtWidgets.QPushButton("测试自定义模型")
        self.model_test_btn.clicked.connect(self.on_model_test_clicked)

        self.model_add_btn = QtWidgets.QPushButton("添加自定义模型")
        self.model_add_btn.clicked.connect(self.on_model_add_clicked)

        self.channel_combo = QtWidgets.QComboBox()
        self.channel_combo.addItems(["飞书", "QQ", "企业微信", "钉钉", "微信"])
        self.channel_combo.currentTextChanged.connect(self._on_channel_changed)

        self.app_id_edit = QtWidgets.QLineEdit()
        self.app_id_edit.setPlaceholderText("appId")

        self.app_secret_edit = QtWidgets.QLineEdit()
        self.app_secret_edit.setPlaceholderText("appSecret")
        self.app_secret_edit.setEchoMode(QtWidgets.QLineEdit.Password)

        self.add_btn = QtWidgets.QPushButton("添加")
        self.add_btn.clicked.connect(self.on_add_clicked)
        self.delete_btn = QtWidgets.QPushButton("删除")
        self.delete_btn.clicked.connect(self.on_delete_clicked)

        self.status_label = QtWidgets.QLabel("")
        self.status_label.setWordWrap(True)

        self.log_box = QtWidgets.QPlainTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMinimumHeight(220)
        self.log_box.setFont(import_qt()[1].QFont("Consolas"))

        model_form = QtWidgets.QFormLayout()
        model_form.addRow("provider：", self.model_provider_edit)
        model_form.addRow("model_id：", self.model_id_edit)
        model_form.addRow("base_url：", self.model_base_url_edit)
        model_form.addRow("api_key：", self.model_api_key_edit)
        model_btn_row = QtWidgets.QHBoxLayout()
        model_btn_row.addWidget(self.model_test_btn)
        model_btn_row.addWidget(self.model_add_btn)

        form = QtWidgets.QFormLayout()
        form.addRow("机器人：", self.channel_combo)
        form.addRow("appId：", self.app_id_edit)
        form.addRow("appSecret：", self.app_secret_edit)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(model_form)
        layout.addLayout(model_btn_row)
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        sep.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(sep)
        layout.addLayout(form)
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.delete_btn)
        layout.addLayout(btn_row)
        layout.addWidget(self.status_label)
        layout.addWidget(self.log_box)
        self.setLayout(layout)

        self._runner = None
        self._model_test_runner = None
        self._current_title = ""
        self._current_action = ""
        self._on_channel_changed(self.channel_combo.currentText())

    def _set_busy(self, busy: bool):
        self.model_provider_edit.setEnabled(not busy)
        self.model_id_edit.setEnabled(not busy)
        self.model_base_url_edit.setEnabled(not busy)
        self.model_api_key_edit.setEnabled(not busy)
        self.model_test_btn.setEnabled(not busy)
        self.model_add_btn.setEnabled(not busy)
        self.add_btn.setEnabled(not busy)
        self.delete_btn.setEnabled(not busy)
        self.channel_combo.setEnabled(not busy)
        self.app_id_edit.setEnabled(not busy)
        self.app_secret_edit.setEnabled(not busy)

    def _mask_api_key(self, s: str) -> str:
        if not s:
            return ""
        if len(s) <= 8:
            return "*" * len(s)
        return f"{s[:2]}{'*' * (len(s) - 6)}{s[-4:]}"

    def _write_model_log_start(self, provider_id: str, model_id: str, base_url: str, api_key: str, action: str):
        self.log_box.clear()
        self.log_box.appendPlainText(f"{action}自定义模型")
        self.log_box.appendPlainText(f"{action}自定义模型中")
        self.log_box.appendPlainText(f"custom-provider：{provider_id}")
        self.log_box.appendPlainText(f"model_id：{model_id}")
        self.log_box.appendPlainText(f"base_url：{base_url}")
        self.log_box.appendPlainText(f"api_key：{self._mask_api_key(api_key)}")

    def _write_action_log_start(self, action: str, channel_title: str, app_id: str, app_secret: str):
        self.log_box.clear()
        self.log_box.appendPlainText(f"{action}{channel_title}")
        self.log_box.appendPlainText(f"{action}{channel_title}中")
        if app_id:
            self.log_box.appendPlainText(f"appID：{app_id}")
        if app_secret:
            self.log_box.appendPlainText(f"appSecret：{app_secret}")

    def _on_channel_changed(self, channel: str):
        need_cred = channel in ("飞书", "QQ", "企业微信", "钉钉")
        self.app_id_edit.setEnabled(need_cred)
        self.app_secret_edit.setEnabled(need_cred)
        if not need_cred:
            self.app_id_edit.setText("")
            self.app_secret_edit.setText("")

    def on_model_add_clicked(self):
        provider_id = self.model_provider_edit.text().strip()
        model_id = self.model_id_edit.text().strip()
        base_url = self.model_base_url_edit.text().strip()
        api_key = self.model_api_key_edit.text().strip()

        if not provider_id or not model_id or not base_url or not api_key:
            self.status_label.setText("custom-provider / model_id / base_url / api_key 不能为空")
            return

        plan = build_custom_model_plan(provider_id, model_id, base_url, api_key)
        self._current_action = "添加"
        self._current_title = plan.title
        self._write_model_log_start(provider_id, model_id, base_url, api_key, "添加")
        self.status_label.setText(f"{plan.title}：配置中…")
        self._set_busy(True)

        self._runner = Runner(plan, "", self._current_action)
        self._runner.log_line.connect(self.log_box.appendPlainText)
        self._runner.finished_run.connect(self._on_finished)
        self._runner.start()

    def on_model_test_clicked(self):
        provider_id = self.model_provider_edit.text().strip()
        model_id = self.model_id_edit.text().strip()
        base_url = self.model_base_url_edit.text().strip()
        api_key = self.model_api_key_edit.text().strip()

        if not provider_id or not model_id or not base_url or not api_key:
            self.status_label.setText("custom-provider / model_id / base_url / api_key 不能为空")
            return

        self._current_action = "测试"
        self._current_title = "自定义模型"
        self._write_model_log_start(provider_id, model_id, base_url, api_key, "测试")
        self.status_label.setText("自定义模型：测试中…")
        self._set_busy(True)

        self._model_test_runner = ModelTestRunner(model_id, base_url, api_key)
        self._model_test_runner.log_line.connect(self.log_box.appendPlainText)
        self._model_test_runner.finished_test.connect(self._on_model_test_finished)
        self._model_test_runner.start()

    def on_add_clicked(self):
        channel = self.channel_combo.currentText()
        app_id = self.app_id_edit.text().strip()
        app_secret = self.app_secret_edit.text().strip()

        if channel in ("飞书", "QQ", "企业微信", "钉钉"):
            if not app_id or not app_secret:
                self.status_label.setText("appId / appSecret 不能为空")
                return
        plan = build_add_plan(channel, app_id, app_secret)
        if plan is None:
            self.status_label.setText("该渠道暂不支持自动配置")
            return

        self._current_action = "添加"
        self._current_title = plan.title
        self._write_action_log_start(self._current_action, self._current_title, app_id, app_secret)
        self.status_label.setText(f"{plan.title}：配置中…")
        self._set_busy(True)

        self._runner = Runner(plan, self._current_title, self._current_action)
        self._runner.log_line.connect(self.log_box.appendPlainText)
        self._runner.finished_run.connect(self._on_finished)
        self._runner.start()

    def on_delete_clicked(self):
        channel = self.channel_combo.currentText()
        app_id = self.app_id_edit.text().strip()
        app_secret = self.app_secret_edit.text().strip()
        plan = build_delete_plan(channel)
        if plan is None:
            self.status_label.setText("该渠道暂不支持自动配置")
            return

        self._current_action = "删除"
        self._current_title = plan.title
        self._write_action_log_start(self._current_action, self._current_title, app_id, app_secret)
        self.status_label.setText(f"{plan.title}：配置中…")
        self._set_busy(True)

        self._runner = Runner(plan, self._current_title, self._current_action)
        self._runner.log_line.connect(self.log_box.appendPlainText)
        self._runner.finished_run.connect(self._on_finished)
        self._runner.start()

    def _on_finished(self, code: int):
        if code == 0:
            self.log_box.appendPlainText(f"{self._current_title}{self._current_action}成功")
            self.status_label.setText(f"{self._current_title}：配置成功")
        else:
            self.status_label.setText(f"{self._current_title}：配置失败，退出码: {code}")
        self._set_busy(False)

    def _on_model_test_finished(self, code: int):
        if code == 0:
            self.log_box.appendPlainText("自定义模型测试成功")
            self.status_label.setText("自定义模型：测试成功")
        else:
            self.status_label.setText(f"自定义模型：测试失败，退出码: {code}")
        self._set_busy(False)
