# 法规依据与报告纠偏

查阅截止 2026-11-19，Asia/Shanghai。对象为药品生产 QC LIMS 的开发规范。相关条文及必要上下文已核对，企业的产品、市场、主本、用途和现场适用性仍须由授权 QC/QA 确认。本文件不宣称穷尽国内外法规，也不证明应用已经验证。

28 条 DEV 规则是项目工程约束。下表区分直接监管要求、条件适用要求、指南与未来参考，不能把具体库、哈希算法、WORM、ABAC 或微服务说成法规点名指定。GAMP 5 付费全文未取得，仅核出版与方法属性。

## 两份报告的采纳与纠正


1. 两报告“规范方向支持合规，但不能证明系统已满足需求、已合规、已通过验证”的总判断正确。开发规约、测试代码与 CI 绿色不足以形成正式质量结论；正式协议、实际执行、偏差处理、复核批准及目标环境均须有可追溯证据。
2. 独立复核报告第 3.3 节第 1 项中的 `21 CFR 11.200(a)(2)(iii)` 不存在。连续受控会话的首次/后续签署位于 `(a)(1)(i)`，非连续会话位于 `(a)(1)(ii)`；`(a)(2)` 是本人使用，`(a)(3)` 是防止他人冒用的管理控制。此为已确认引用错误，应记录勘误，保留源报告原件。
3. URS-610 中“人工更改”不能一概判为法规禁止。国内《计算机化系统》附录第 16 条允许有授权、批准和理由的关键数据更改；GMP 第 161 条要求原信息仍可辨。应规范为禁止无痕覆盖原始值、禁止改写已批准标准版本；受控更正以新修订、前后值、原因、人员、时间、批准和相关签名处理完成。原 URS 的业务意图由 QA/QC 做受控澄清。
4. URS-704 的结果采用可以设计为有科学依据、调查和批准的采用关系；不能做自动取合格值、删除 OOS、重测直至合格或覆盖首次结果。FDA OOS 指南主要适用于化学检验，微生物等项目须另行确认对应方法与 SOP，不能机械照搬化学重测策略。
5. 非生物识别电子签名的“两种不同识别组成部分”不等于一律需要两套密码、手机 OTP 或现代 MFA 的两种因素；登录、持续会话与签署分别设计。也不能认为普通 JWT、SSO 登录或按钮确认自然满足电子签名。
6. 欧委会 EudraLex 现行目录在本次查阅时仍列 Annex 11 为 2011 修订、Chapter 4 为 2011、Annex 15 为 2015；2025 年 Chapter 4/Annex 11/Annex 22 咨询页仍标 Draft。可以做未来准备，但不能当现行强制条款。
7. Annex 19 修订在官方目录/公告明确为 2026-09-24 起适用。若欧盟市场与留样模块适用，需要纳入功能适用清单；第 9.5 节允许数字留样是对特定再包装情况且需主管机关事先同意的条件性安排，不可泛化为所有留样都用照片代替实物。
8. FDA 2026 年 2 月 CSA 最终指南确实存在，其范围是医疗器械生产和质量管理系统软件，替代 2025-09-24 版。不能用它主张药品 LIMS 免除验证。其风险方法可作为参考并明确来源属性。
9. 《网络安全法》2025 年修正自 2026-01-01 生效，现行等级保护与网络日志义务在第 23 条，不是旧版第 21 条。网络运行/安全事件相关日志不少于六个月；GMP 审计追踪应按质量记录保留策略保存，不能降为统一六个月。用户人数不能直接决定等保级别。
10. “原件不可变”“哈希”“WORM”“审计链”是不同层次的控制。上述已核法规规定完整性、访问限制、更改可发现、保留与可读等目标，没有指定 HB-Lims 必须选某款对象存储、某种哈希算法、微服务、ABAC、区块链或 JWT。项目可以批准加严实现，但必须标为项目工程选择，不能说成法规点名要求。

## 相关原文和适用边界


| ID | 文件和已核位置 | 性质与适用边界 | 本轮核验结果及可承接开发控制 |
|---|---|---|---|
| RG-CN-01 | 中国药品 GMP 第 138–148、151–163、240–246 条 | 国内药品生产质量活动的部门规章；具体产品附录另核 | 风险、预先批准的验证方案、执行记录、报告批准、文件版本、更正留原值、记录保留与软件变更控制；可直接承接项目规范 |
| RG-CN-02 | 2015 年第 54 号《计算机化系统》附录第 1、3–9、11–23 条 | GMP 配套附录；覆盖应用、基础设施、人员和程序 | 应用验证/基础设施确认、迁移数值语义不变、关键输入复核、授权与更正理由、备份恢复和故障处置；HBOS 可缩减应用边界但身份接口依赖不能从验证影响中消失 |
| RG-CN-03 | 同号《确认与验证》附录第 1–10、50–53 条 | 国内确认验证活动 | 生命周期规划；第三方方案、数据、报告由企业审核批准；未完成阶段有条件推进必须有影响评估和真实批准；不能由 Agent 虚填批准 |
| RG-CN-04 | 2020 年第 74 号《药品记录与数据管理要求（试行）》第 2、5–11、17–23、26–29 条 | 境内相关药品活动产生、应向监管提供的记录与数据 | 操作/系统管理职责分离、唯一用户、操作追踪、可信时间、数据及元数据备份、验证恢复、退役可读、基准记录定义；2020-12-01 施行 |
| RG-CN-05 | 《电子签名法》2019 修正，第 5、6、13–16 条 | 电子签名法律框架；可靠性与特定用途分别论证 | 专属控制、变更可发现、长期可读等目标须有真实实现和程序；不把数据库 hash 与姓名时间字段直接认定为法定可靠电子签名；需要第三方认证时依法选择服务 |
| RG-CN-06 | 《个人信息保护法》第 3、6、13、19、21、47、51、55 条 | 员工账号、签名、培训资质等个人信息处理 | 最小必要与处理依据；受托方责任；安全控制；生命周期保留/删除；触发条件下影响评估；不统一依赖同意，不因离职删除仍需保存的质量身份关系 |
| RG-CN-07 | 《网络安全法》2025 修正，第 2、23、24 条 | 境内网络建设运营维护使用；按企业实际网络运营角色落实 | 等保责任、网络日志不少于六个月、重要数据备份/加密、漏洞处置；级别须依边界和风险评估，不能直接写二级或三级 |
| RG-US-01 | 21 CFR Part 11 §§11.1、11.3、11.10、11.30、11.50、11.70、11.100、11.200、11.300 | 美国 FDA 受监管记录和电子签名条件适用；不是所有电子记录一律适用 | 验证、授权、审计、完整副本、保留、签名关联及凭据管理；电子签名法定义务和企业承诺程序也要覆盖。eCFR 显示 Title 21 更新至 2026-11-17，未将抓取日冒充更新日 |
| RG-US-02 | 21 CFR 211.68(b)、211.180(a–d)、211.194(a–e) | 成品药 cGMP 适用；原料药另评估 FD&C Act/ICH Q7 路径 | 受权变更、输入输出核查、精确完整备份、完整原始检验记录、计算与独立复核；记录类别/起算点不同，不统一五年删除 |
| RG-US-03 | FDA Drug CGMP DI Q&A，2018，第 1、2、4、5、7–10、12、14 问 | 非约束性指南，解释相关药品 cGMP 义务 | 全数据与必要元数据、动态原始格式、审计复核、共享账号风险；可作为工程设计/风险分析依据，勿标独立法律强制 |
| RG-US-04 | FDA Investigating OOS，2022，§I、IV.B–C、V | 非约束性指南；主要化学检验范围 | 合理重测策略、调查与全部结果保留、不得重测到合格；业务规范采用须与厂内 SOP 一致 |
| RG-US-05 | FDA CSA 2026，官方范围说明及最终指南 §III | 医疗器械生产/QMS 软件指南 | 药品 LIMS 不是此指南直接豁免对象；仅可参考风险思路 |
| RG-EU-01 | EudraLex 目录及 Annex 11 2011，§1–17 | 欧盟药品 GMP 框架下，按市场/产品/质量协议适用 | 生命周期、需求追踪、异常/边界测试、迁移、输入、备份、审计复核、配置变更、周期评价、签名、业务连续性与归档 |
| RG-EU-02 | Chapter 4 2011，§4.1–4.12 | 欧盟适用时的 GMP 文档要求 | 主本、纸电关系、受控版本、当时记录、保留；批记录有效期后一年或 QP 认证后五年取较长，其他记录另定；不能全部套五年 |
| RG-EU-03 | Annex 15 2015，原则、§1、2、3、4 | 药品生产确认验证；对原料药为补充性可选指南不额外增加 Part II 要求 | 文件关系、批准方案、偏差、阶段放行、变更影响和必要再验证；IQ/OQ 可合理组合，不能机械要求每个小改动重做全套 |
| RG-EU-04 | 2025 Chapter 4/Annex 11/Annex 22 咨询页面 | 草案，未来准备参考 | 未将草案当现行法规；尤其开发 Agent 的使用不等于产品内已上线 AI 质量决策模块 |
| RG-EU-05 | Annex 19 修订，2026-09-24 起适用；§9.5 | 留样/参考样与欧盟市场触发 | 留样模块单独扩展，特殊再包装数字留样条件不可泛化 |
| RG-GD-01 | PIC/S PI 041-1，2021-07-01，§9 相关 | 面向检查员的数据完整性指南，也是行业参考 | 原系统/接口风险、供应商、测试、迁移、补丁、周期评价、审计复核；不是单独通用法律 |
| RG-GD-02 | GAMP 5 第二版，ISPE 2022 发行信息和 What is GAMP | 行业方法；公开页面仅支持定位与性质 | ISPE 明确其不是规定式方法或标准；付费全文未取得，不能声称逐页审阅或引用未核细条 |

### 官方链接

- RG-CN-01：https://www.samr.gov.cn/zw/zfxxgk/fdzdgknr/bgt/art/2023/art_d5e1dbaa8f284277a5f6c3e2fc840d00.html
- RG-CN-02：https://amr.hainan.gov.cn/himpa/yprz/jchc/ypgmpxcjc/201710/t20171016_460798.html
- RG-CN-03：https://amr.hainan.gov.cn/himpa/yprz/jchc/ypgmpxcjc/201710/t20171016_460801.html
- 2015 第 54 号公告身份与施行时间：https://www.ccfdie.org/zryyxxw/zxdt/webinfo/2017/01/1485585739044109.htm
- RG-CN-04：https://www.ccfdie.org/cn/yjxx/yphzp/webinfo/2020/07/1592159028811276.htm
- RG-CN-05：https://www.miit.gov.cn/jgsj/zfs/fl/art/2022/art_e3f623f70c23497e88a941170093446a.html
- RG-CN-06：https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm
- RG-CN-07：https://www.cac.gov.cn/2025-12/29/c_1768735112911946.htm
- RG-CN-07 修正决定和生效日：https://www.cac.gov.cn/2025-10/29/c_1763461514768457.htm
- RG-US-01：https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-11
- RG-US-02：https://www.ecfr.gov/current/title-21/chapter-I/subchapter-C/part-211/subpart-D/section-211.68
- RG-US-02：https://www.ecfr.gov/current/title-21/chapter-I/subchapter-C/part-211/subpart-J/section-211.180
- RG-US-02：https://www.ecfr.gov/current/title-21/chapter-I/subchapter-C/part-211/subpart-J/section-211.194
- RG-US-03：https://www.fda.gov/media/119267/download
- RG-US-04：https://www.fda.gov/media/158416/download
- RG-US-05：https://www.fda.gov/regulatory-information/search-fda-guidance-documents/computer-software-assurance-production-and-quality-management-system-software
- RG-EU 现行目录：https://health.ec.europa.eu/medicinal-products/eudralex/eudralex-volume-4_en
- RG-EU-01：https://health.ec.europa.eu/document/download/8d305550-dd22-4dad-8463-2ddb4a1345f1_en
- RG-EU-02：https://health.ec.europa.eu/document/download/104b3eb8-81a7-4858-9419-cb06562adb66_en?filename=chapter4_01-2011_en.pdf
- RG-EU-03：https://health.ec.europa.eu/document/download/7c6c5b3c-4902-46ea-b7ab-7608682fb68d_en?filename=2015-10_annex15.pdf
- RG-EU-04：https://health.ec.europa.eu/consultations/stakeholders-consultation-eudralex-volume-4-good-manufacturing-practice-guidelines-chapter-4-annex_en
- RG-EU-05：https://health.ec.europa.eu/latest-updates/eudralex-volume-4-reference-and-retention-samples-revised-applicable-24-september-2026-2026-06-24_en
- RG-EU-05 正文：https://health.ec.europa.eu/document/download/831d392e-bcc4-4552-8011-2b724b8655de_en?filename=c2026-4135_en_act_en.pdf
- RG-GD-01：https://picscheme.org/docview/4234
- RG-GD-01 身份：https://picscheme.org/en/news/adoption-and-entry-into-force-of-pics-guidance-on-good-pract
- RG-GD-02：https://ispe.org/initiatives/regulatory/what-gamp
- RG-GD-02 版次：https://ispe.org/publications/guidance-documents/gamp-5-guide-2nd-edition/

## 重新评估触发

主体/厂区、产品/市场、记录主本、签名用途、方法或模块、外部接口、部署区域/数据流、法规版次变化均须评估；欧盟留样、微生物/无菌、稳定性等模块还需补相应专门依据。官方链接可更新，冻结候选前复核适用版本并保存受控引用。

国内部分原发布附件抓取不稳定，相关条文以海南省药品查验中心和国家药监局直属机构官方转载核验；不以检索未发现更新断言全部法规无变化。
