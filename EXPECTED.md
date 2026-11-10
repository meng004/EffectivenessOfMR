# 待归档的复盘材料

本仓库当前只含文档与核验记录。读者要复盘正文的读数，还需要下列三类材料；下表按附录D.1 的入口列出，用于向材料持有方索取完整数据包。

## 一、实验代码

| 对象 | 需要的内容 | 对应正文 |
|---|---|---|
| 原科学载体 | `evidence/v25_N1_final_review_package.zip`；SHA `45dc02cb2223aa5f5bc9bb2622f289b251a1e190fe9ae145a05464171c3ec15e`（内含逐端字段与库存索引；历史评审内容不取） | 附录D.1 |
| 冻结 CRAM16 PFD 系数 | `supplementary/cram/e1_original.zip` → `phase27_pilot/package/coefficients.json`（α₀、α_j、θ_j 的精确有理值与 binary64 十六进制解释）；SHA `ff6213f17b36a07a9ea974895b34d5f4b52cb65f654313c591d8fe2a6576fc4c` | §4.7.1、附录D.2 |
| ONIX 调用与适配层 | 输入装配、工作矩阵替换（EZ／ET 注入）、结果采集；篡改路径与采集路径同一 | §4.2、§4.4 |
| OpenMOC 模型与求解配置 | 几何、核数据、源、边界、迭代控制（收敛阈 1e−8、1000 次上限） | §4.3、§4.7.3 |
| 证书与比较脚本 | `checker.py`（逐移位残差与 E 的保存算术）、`check_saved_slice.py`、`revision_checks.json` 生成逻辑 | 附录D.2 |
| 静态核验 | `verify_*_static.py`（已在 `records/`） | — |

## 二、实验对象

| 对象 | 需要的内容 | 对应正文 |
|---|---|---|
| 三状态矩阵组 | A_N、A_ε、2A_N 的 binary64 值；共同零源；初值对 S1／S2／S3 | §4.7.1、§4.8.1 |
| 五状态模型 | A₀、A₁ 与初值 u=e₅、v=e₅+e₁；四场 (A₀,u)、(A₀,v)、(A₁,u)、(A₁,v) | §4.7.2、附录H |
| MOC 输入 | 单群两区纯吸收、单群两区散射反馈、两群两区 1→2 下散射的几何／核／源；M1—M3 的源方向 | §4.7.3、附录J |
| IPF16 | C1 批冻结系数与因子顺序 `freeze.json` | §4.8.2、附录I |

## 三、实验结果

| 批次 | 需要的内容 | 当前档案 | 对应正文 |
|---|---|---|---|
| E1 | 54 端 `input.json`／`output.json`／`certificate.json`；端 ID 与字段索引 `v26_result_index.json` | `supplementary/cram/e1_original.zip` | §4.8.2、附录D.1 |
| C1 | 54 端 `worker.json`／`certificate.json`；`freeze.json` | `supplementary/cram/c1_original.zip` | §4.8.2、附录I |
| EZ／ET 最小链 | 系数、参考 `reference.json` 及各条件输出与证书 | `supplementary/cram/ez_revision_evidence_private.zip` | §4.8.1、附录D.2 |
| T-M1 | `scale-comparison.json`、`sup-comparison.json` 及端 snapshot／reference | `M1-M3-existing-raw-evidence-slice.tar.gz` | §4.8.3、附录J |
| T-M2／T-M3 | 各端 `certificate.stdout` 与 snapshot；有限工作／声明目标、E／W／ρ_int | 同上 tar | §4.8.3、附录J |
| F1／EZ | 输入、输出、参考、证书与事后同阈分析 | `F1_EZ实验补充证据.tar.gz`；SHA `687797139f66a701c4e2a72c0f6a30f0756e266c24995521f3be95fac9b0e4fd` | 附录C、D.1 |
| 2A | 两调用／16 shift 与故障目标证书 | `cram-2a-real-evidence-20261103.tar.gz`；SHA `38e4f60aadd4f8605390147c72c854354cd531d394e5065fb408bfcb2385a0d3` | 附录C、D.1 |
| 多路径 | 四输出字节及单输入／配对参考 | `CRAM_多路径_四场评审材料.tar.gz`；SHA `ec7cdc3154d256c62cf36dffb971d773b403030ca517233ed64d2db8a156be9d` | 附录H、D.1 |
| MOC 六场 | 源／构造／输出记录副本 | `MOC_健康与源变异_评审材料.tar.gz`；SHA `4bd58aaadc09db77e9c6380e3249705d58d6222e3f3b7c13bd4f92b0ec7c9066` | 附录C、D.1 |
| 连续参考 | 独立连续参考；对外提供需另核许可 | 作者保存；SHA `d8ae5786c4a3c0e52e79cfd786684491347bdc4b4de22a67585e5244ea4b4136` | 附录D.1 |

## 索取时要说明的四件事

1. **不含什么**：历史评审归档（`v25_N1_final_review_package.zip`、`v25_ARS全新评审_完整交付包.zip`）不归档。
2. **许可**：连续参考、IPF16 冻结系数、核数据可能受第三方许可限制，需材料持有方确认可否公开。
3. **可核层级**：提供原始端记录即支持"保存字节读取 + 精确算术复核"；证书重生、程序重放和运行身份认证是另外三层，正文附录D.3 已声明未完成。
4. **体积**：E1／C1／M1—M3 四个包合计为主要体积，建议放 Release 附件或 Git LFS，不直接进主分支。
