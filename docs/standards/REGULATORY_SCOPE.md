# REG-V1 法规适用、系统边界与记录主本（C01）

本文件区分来源要求、项目控制和待QA决定事项。Owner认可将这些控制纳入开发；尚无项目适用性或验证批准。查阅日期2026-11-16，不是法律意见或监管认证。

## REG-01 先建立适用矩阵

每条记录至少填写：文件及版本/条款、法律或指南性质、产品/API或制剂、市场/厂区、记录类型、适用理由、不适用理由（如有）、关联URS/控制、责任人、受控批准引用、复核日期。只有中文法规名字或Part11勾选不算完成。URS正文主体与新乡项目差异须批准补充，不改原始DOCX。

| ID | 来源和定位 | 使用边界 |
| --- | --- | --- |
| CN01 | 药品GMP（2010年修订），记录/检验/保存相关条款 | 中国生产质量活动基础；按具体产品与记录确认 |
| CN02 | 《计算机化系统》附录第3–6、9、11、13–23条 | 生命周期风险、供应商协议、应用验证/设施确认、主本、迁移和恢复 |
| CN03 | 《药品记录与数据管理要求（试行）》第6、13、15、21–27条 | 原始记录、版本、校时、权限分离、元数据和保存 |
| US01 | 21 CFR Part11 §§11.1/11.10/11.50/11.70/11.100/11.200/11.300 | 根据适用监管记录判断；不是软件产品证书 |
| US02 | FDA/ICH Q7 §5.4、6.6、11 | 原料药活动重点评估；指南不与法规层次混同 |
| US03 | 21 CFR 211.194 | 成品制剂等适用时；不无差别套用到全部API活动 |
| US04 | FDA药品CGMP数据完整性问答（2018），Q7–Q12 | 审计复核、动态数据、原始记录的监管解释 |
| US05 | FDA OOS调查指南（2022），III–V | 调查/复测原则；OOT/AR定义仍需公司确认 |
| EU01 | EU GMP Annex11（官网当前列表为2011修订），§§3–4/7/9–17 | 欧盟市场/质量协议适用时；2025咨询稿不当生效要求 |
| IND01 | GAMP5第二版 | 行业方法，不是法规；2026-11-20已收到中文参考材料并审阅相关完整章节，翻译授权未确认，详见[来源评估](sdlc-validation/SOURCE_ASSESSMENT.md) |

稳定性、留样、环境监测及无菌产品扩展时，由QA继续检查相关专门要求；本矩阵不是全部法规穷尽清单。欧盟官网另列2026-09-24适用的Annex19修订入口，应在留样域适用性评估时核查具体范围，不自动套给本项目所有活动。

## REG-02 纸电主本和独立系统

按记录类型指定纸质/电子/混合主本、并行期、核对责任、切换条件和批准者。技术演示、约一个月模块试用与正式质量使用分开；未授权不得以电子记录替代既有正式记录。纸质主本也不能成为丢弃电子原始数据或元数据的理由。

独立LIMS验证范围涵盖应用、受控配置、数据、签名、审计、基础设施和关键外部接口。HBOS只提供链接时不牵入全部运营模块；若承担认证，其接口和变更影响必须评估。身份、ERP/WMS/QMS、DMS/TMS、CDS的故障与回执都应在相应范围内验证。

## REG-03 责任与变更

内部开发负责可复现工程与技术证据；验证服务商按合同执行/见证及记录偏差；公司QC/QA/Owner负责需求、风险接受和最终批准。供应商参与开发时仍通过我方仓库PR，不以验证身份自批其开发成果；独立性与补偿控制写入质量协议。

不得以技术文件暗改URS-610的修改语义、URS-704的结果采用规则、URS-101的浏览器范围或URS-105的保留解释；在差异单中明确提出受控实现及批准。两项身份组成不等于法规要求两套密码；证书签名亦非所有场景唯一实现。URS的具体约定需要保持追踪，必要变更由QA/Owner审批。

## REG-04 验收与来源

C01验收：有实际适用矩阵、主体补充、记录主本决定和批准引用；不允许把草案/行业介绍当法规已生效，不允许用Owner接受规划替代QA签署。

官方资料（2026-11-16复核主要入口；逐条适用性仍待QA）：
- CN01：https://www.samr.gov.cn/zw/zfxxgk/fdzdgknr/bgt/art/2023/art_d5e1dbaa8f284277a5f6c3e2fc840d00.html
- CN02：https://amr.hainan.gov.cn/himpa/yprz/jchc/ypgmpxcjc/201710/t20171016_460798.html
- CN03：https://www.ccfdie.org/cn/yjxx/yphzp/webinfo/2020/07/1592159028811276.htm
- US01：https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-11
- US02：https://www.fda.gov/regulatory-information/search-fda-guidance-documents/q7-good-manufacturing-practice-guidance-active-pharmaceutical-ingredients-guidance-industry
- US03：https://www.ecfr.gov/current/title-21/chapter-I/subchapter-C/part-211/subpart-J/section-211.194
- US04：https://www.fda.gov/regulatory-information/search-fda-guidance-documents/data-integrity-and-compliance-drug-cgmp-questions-and-answers
- US05：https://www.fda.gov/regulatory-information/search-fda-guidance-documents/investigating-out-specification-oos-test-results-pharmaceutical-production-level-2-revision
- EU01：https://health.ec.europa.eu/medicinal-products/eudralex/eudralex-volume-4_en
- IND01：https://ispe.org/publications/guidance-documents/gamp-5-guide-2nd-edition/
