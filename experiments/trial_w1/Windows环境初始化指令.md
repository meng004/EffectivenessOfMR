# Windows 实验环境初始化指令（trial_w1）

## 目标

在一台 Windows 电脑上，从零准备好运行[实验设计_第1与3项.md](实验设计_第1与3项.md)所需的全部环境，到「OpenMC 已构建、Python 包可编辑安装、cosmic-ray 可用、健康基线 MR 全部通过」为止。

## 步骤

### 第 1 步：装 WSL2 与 Ubuntu（PowerShell，管理员）

```powershell
wsl --install -d Ubuntu-24.04
```

重启电脑，首次打开 Ubuntu 时设置用户名和密码。

验证：

```powershell
wsl -l -v
```

应看到 `Ubuntu-24.04`，VERSION 列为 `2`。

### 第 2 步：在 Ubuntu 里初始化 git 并取回实验文件

```bash
sudo apt-get update && sudo apt-get install -y git
git config --global core.autocrlf input
git clone --branch trial-w1 https://github.com/meng004/EffectivenessOfMR.git ~/EffectivenessOfMR
mkdir -p ~/mrtrial && cp -r ~/EffectivenessOfMR/experiments/trial_w1/harness ~/mrtrial/
```

验证：

```bash
file ~/mrtrial/harness/setup_wsl.sh
```

输出中**不能**出现 `CRLF`。出现就执行 `sed -i 's/\r$//' ~/mrtrial/harness/*.sh ~/mrtrial/harness/*.py`。

### 第 3 步：构建 OpenMC 与 Python 环境（约 20–40 分钟）

```bash
bash ~/mrtrial/harness/setup_wsl.sh 2>&1 | tee ~/mrtrial/setup.log
echo 'export PATH=$HOME/mrtrial/local/bin:$PATH' >> ~/.bashrc && source ~/.bashrc
```

验证（三条都要满足）：

```bash
tail -3 ~/mrtrial/setup.log
```

- 有 `OK editable`。

```bash
openmc --version | head -1
```

- 显示 `0.15.2`。

```bash
source ~/mrtrial/venv/bin/activate && cosmic-ray --version
```

- 有版本号输出。

### 第 4 步：核对按记忆编写的 API（约 30 分钟）

执行[实验设计_第1与3项.md](实验设计_第1与3项.md) §3.2 的三条 grep；按源码修正 `~/mrtrial/harness/mrlib.py` 中 `build_A_openmc` 与 `solve`。

验证：

```bash
cd ~/mrtrial/harness && python cram_case.py /tmp/smoke.json
```

正常打印一个哈希和秒数，不报错。

### 第 5 步：健康基线

```bash
cd ~/mrtrial/harness && for i in 1 2 3; do python run_mr.py; done; python run_oracle.py; echo "exit=$?"
```

验证：15 行 `MRVERDICT ... pass`，1 行 `ORACLE pass`，`exit=0`。

到此初始化完成，接着按实验设计文档 §2.3、§3.5 起执行。

## 失败时

| 现象 | 处理 |
|---|---|
| `wsl --install` 报虚拟化未开启 | 进 BIOS 打开 Intel VT-x / AMD-V，再重试 |
| 第 3 步 cmake 找不到 HDF5 | `sudo apt-get install -y libhdf5-dev pkg-config` 后重跑脚本（脚本可重入，已克隆的源码不会重下） |
| 克隆 GitHub 超时 | 配置代理：`git config --global http.proxy http://<主机IP>:<端口>`；WSL 访问 Windows 代理需用主机 IP，不是 127.0.0.1 |
| C++ 核构建失败 | 记录报错。先跳过 C++：`source ~/mrtrial/venv/bin/activate && pip install -e ~/mrtrial/openmc scipy cosmic-ray coverage`，CRAM 和第 3 项都只用 Python 层 |
| 第 5 步某条 MR 在健康代码上失败 | 不要改 MR，按实验设计 §3.4 整体放宽 `RTOL` 并记录；这是一个误报实例，写进 `notes.md` |

## 优点、缺点与取舍

| 选择 | 优点 | 缺点 | 为什么这样取 |
|---|---|---|---|
| WSL2，不用原生 Windows | OpenMC 构建链和 cosmic-ray 在 Linux 下最稳；脚本与之前的 Linux 构建经验一致 | 多一层虚拟化；首次安装需重启、可能要开 BIOS 虚拟化 | 原生 Windows 编译 OpenMC 的 C++ 核需要自行处理 HDF5 与 MSVC 兼容，风险远大于装 WSL |
| 文件放 WSL 内部 `~/mrtrial`，不放 `/mnt/c` | 构建和几千次变异运行快一个数量级 | 在 Windows 资源管理器里不直观（可用 `\\wsl$\Ubuntu-24.04\home\<用户>` 访问） | 第 3 项耗时以小时计，I/O 速度决定能否一晚跑完 |
| 从 git 分支 `trial-w1` 克隆，`autocrlf input` | 版本可追溯；避免 Windows 换行破坏 bash 脚本 | 需要能访问 GitHub | 用 U 盘拷贝也行，但换行风险更高、版本不可追溯 |
| 可编辑安装 `pip install -e` | cosmic-ray 改的就是 import 加载的源码，变异真正生效 | 变异中断时源码可能残留修改 | `run_cr.sh` 每轮后用 `git diff --quiet` 检查，残留即停止；恢复用 `git -C ~/mrtrial/openmc checkout .` |
| 健康基线放进初始化 | 尽早暴露 API 不符与误报 | 初始化多花约 10 分钟 | 这一步不过，后面数小时的变异运行全部无效 |
| 不预装 Docker | 少一个组件 | 环境不如容器可复现 | `env.txt` 记录 pip freeze 与提交号，对一周可行性试验已足够；正式实验再考虑容器化 |

## 未验证

- 本指令与脚本只在 macOS 上做过语法检查与 MR 逻辑自检，没有在 Windows 或 WSL 上实际运行过。
- `mrlib.py` 中 OpenMC API 写法、cosmic-ray 命令与数据库列名均未在实装环境验证，见第 4 步与实验设计 §3.7–3.8。
