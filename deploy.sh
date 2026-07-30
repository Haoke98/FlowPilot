#!/bin/bash
# ============================================================
# FlowPilot 快速部署脚本 (CentOS 7.9 x86_64)
# 无需预装 Python，自动下载便携版 Python 并安装 FlowPilot
# 用法: bash deploy.sh [--port 7890] [--mode direct|smart] [--token TOKEN]
# ============================================================
set -e

INSTALL_DIR="${HOME}/.pflowc-runtime"
PYTHON_URL="https://github.com/indygreg/python-build-standalone/releases/download/20241002/cpython-3.12.7+20241002-x86_64-unknown-linux-gnu-install_only.tar.gz"

PORT="${PORT:-7890}"
MODE="${MODE:-direct}"
TOKEN=""
SETUP_SYSTEMD=""

usage() {
    echo "FlowPilot 快速部署脚本"
    echo "  bash deploy.sh [--port 7890] [--mode direct] [--token xxx] [--systemd] [--install-only]"
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --port) PORT="$2"; shift 2 ;;
        --mode) MODE="$2"; shift 2 ;;
        --token) TOKEN="$2"; shift 2 ;;
        --systemd) SETUP_SYSTEMD=1; shift ;;
        --install-only) INSTALL_ONLY=1; shift ;;
        -h|--help) usage ;;
        *) shift ;;
    esac
done

# ── 1. 下载便携 Python（如未安装）─────────────────────────
if [[ ! -f "${INSTALL_DIR}/bin/python3" ]]; then
    echo ">>> 下载便携 Python (约30MB)..."
    mkdir -p "${INSTALL_DIR}"
    curl -fsSL "${PYTHON_URL}" | tar xz -C "${INSTALL_DIR}" --strip-components=1
    echo ">>> Python 就绪: $(${INSTALL_DIR}/bin/python3 --version)"
fi

PYTHON="${INSTALL_DIR}/bin/python3"
PIP="${INSTALL_DIR}/bin/pip3"

# ── 2. 安装 FlowPilot ─────────────────────────────────────
echo ">>> 安装 FlowPilot..."
${PIP} install -q git+https://github.com/Haoke98/FlowPilot.git

# ── 3. 配置 ───────────────────────────────────────────────
CONFIG_DIR="${HOME}/.PFlowC"
mkdir -p "${CONFIG_DIR}"

if [[ -n "${TOKEN}" ]]; then
    echo ">>> 写入配置 (mode=${MODE}, port=${PORT}, token=***)"
    cat > "${CONFIG_DIR}/config.json" << EOF
{
  "port": ${PORT},
  "mode": "${MODE}",
  "routing_strategy": "round_robin",
  "upstreams": [],
  "auth": {
    "enabled": true,
    "username": "",
    "password": "",
    "tokens": ["${TOKEN}"]
  },
  "bypass_domains": ["127.0.0.1", "192.168.0.0/16", "172.16.0.0/16", "10.0.0.0/8"]
}
EOF
else
    echo ">>> 交互式配置:"
    ${PYTHON} -m PFlowC.main setup
fi

[[ -n "${INSTALL_ONLY}" ]] && echo ">>> 安装完成，跳过启动" && exit 0

# ── 4. 启动 ───────────────────────────────────────────────
echo ">>> 启动 FlowPilot (mode=${MODE}, port=${PORT})"
nohup ${PYTHON} -m PFlowC.main server --mode "${MODE}" --port "${PORT}" \
    > "${CONFIG_DIR}/logs/server.log" 2>&1 &
echo ">>> PID: $!"
sleep 2
${PYTHON} -m PFlowC.main version 2>/dev/null || true
echo ">>> 完成! 代理地址: $(hostname -I | awk '{print $1}'):${PORT}"

# ── 5. systemd（可选）─────────────────────────────────────
if [[ -n "${SETUP_SYSTEMD}" ]]; then
    SERVICE_FILE="/etc/systemd/system/pflowc.service"
    cat > "${SERVICE_FILE}" << EOF
[Unit]
Description=FlowPilot Proxy Router
After=network.target

[Service]
Type=simple
ExecStart=${PYTHON} -m PFlowC.main server --mode ${MODE} --port ${PORT}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    systemctl enable --now pflowc
    echo ">>> systemd 服务已安装并启动"
fi
