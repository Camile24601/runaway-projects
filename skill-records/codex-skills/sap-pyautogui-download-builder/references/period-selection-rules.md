# 轻量期间选择脚本规则

## 适用场景

当用户要求新建完整 SAP 下载项目，且没有明确提供现成 `01-公司期间选择.py` 时，默认生成轻量期间选择脚本。该脚本负责：

- 初始化或读取 `d:/sap_download_config.ini`。
- 初始化或读取 `1.原始数据/sap_business_config.ini`。
- 录入并保存 SAP 账号、密码、公司代码、期间。
- 将参数提供给后续 SAP 下载脚本。
- 按上一账期备份项目数据目录。

## 默认参数

若用户未特别说明，使用：

```python
root_dir = "1.原始数据"
save_dir = "2.运行结果"
backup_dir = "0.数据备份"
login_file = r"d:/sap_download_config.ini"
login_section = "FI_FB"
business_file = os.path.join(root_dir, "sap_business_config.ini")
```

`business_section` 必须按项目填写，例如 `FI_AP051`。如果用户给了 SAP 下载脚本的 `business_section`，期间选择脚本必须使用同一个值。

## 默认公司代码

从当前工作目录最后一级名称中提取纯数字片段作为默认公司代码：

```python
default_com = next((s for s in os.getcwd().split('\\')[-1].split('-') if s.isdigit()), '')
```

如果项目目录不是 Windows 反斜杠路径，也可兼容 `os.path.basename(os.getcwd())`，但不要为了美化而重构整段脚本。

## 配置初始化

登录配置缺失时自动创建：

```python
login_config[login_section] = {'SAP账号': 'FI000', '密码': '000000'}
```

业务配置 section 缺失时自动创建：

```python
business_config[business_section] = {
    'com_lists': default_com,
    'fin_period': this_month,
}
```

这些默认值是占位初始值；用户提交后要写回真实输入。

## 输入窗口

输入框顺序固定为：

1. `SAP账号`
2. `密码`
3. `公司代码`
4. `期间`

密码框必须：

- `show="*"`。
- 默认显示 `******`。
- 如果用户未改动 `******`，写回原密码。

期间校验：

- 接受 `YYYYMM`。
- 接受 `YYYYM` 并补为 `YYYY0M`。
- 不合法时弹窗提示，不写配置。

键盘绑定：

- 根窗口绑定 `<Key-Return>`。
- 根窗口绑定 `<KP_Enter>`。
- 每个输入框也绑定 `<Key-Return>` 与 `<KP_Enter>`。

## 写回配置

用户提交后：

- 更新 `login_config[login_section]['SAP账号']`。
- 更新 `login_config[login_section]['密码']`。
- 更新 `business_config[business_section]['com_lists']`。
- 更新 `business_config[business_section]['fin_period']`。
- 使用 `utf-8-sig` 写回，保持与下载脚本读取方式一致。

打印配置时不得明文打印密码。可以复制用户样例中的 `date_input_copy[1]='*'` 或直接只打印账号、公司代码、账期。

## 备份规则

备份期间为当前输入期间的上一个月：

```python
current_period = datetime.strptime(fin_period, '%Y%m')
previous_period = (current_period - relativedelta(months=1)).strftime('%Y%m')
```

默认备份到：

```python
target_backup_dir = os.path.join("0.数据备份", previous_period)
```

默认备份：

- `1.原始数据`
- `2.运行结果`

如果用户项目存在中间过程表目录，则增加：

- `2.中间过程表`
- 或用户指定的其他目录

同一备份期间下目标目录已存在时，母版默认先 `shutil.rmtree()` 再 `shutil.copytree()`。生成脚本时要在交付说明中提醒这一点。

## 生成时少问的问题

为减少人工修改，除非缺失会导致脚本不可用，否则不要反复追问：

- 未提供 `login_section` 时默认 `FI_FB`。
- 未提供备份目录时默认 `0.数据备份`。
- 未提供备份清单时默认 `1.原始数据` 与 `2.运行结果`。
- 未提供默认账号时使用 `FI000` / `000000` 作为初始化占位。

必须确认或保留 `TODO`：

- `business_section`。
- 项目 `cd` 路径。
- 是否存在必须备份的中间过程目录。
