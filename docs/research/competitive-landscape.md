# 制药QC LIMS对标研究

调研日期2026-11-16。方法为厂商官网、官方产品资料及公开案例的案头研究；未购买、登录实测、询价或独立验证厂商宣传。下列“借鉴”是本项目设计建议，不是产品能力打分或采购结论。

| 对标 | 官方资料呈现的方向 | HB-Lims应借鉴 | 对应需求 | 不宜直接照搬 |
| --- | --- | --- | --- | --- |
| LabWare | 制药QA/QC、样品/批次、稳定性与环境监测 | 统一样品全生命周期，稳定性条件/时间点/取样数量，监测点位趋势 | 200–800、1700–1807 | 全量企业级平台配置复杂度，未经验证的市场排名和节省比例 |
| LabVantage Pharma | 制药预配置场景及LIMS/ELN/LES/SDMS产品组合 | 分清业务台账、检验步骤、实验记录、原始数据四种责任；主数据与验证材料同步建设 | 500、600–624、1200–1210、2107–2109 | 把厂商预验证当成本厂已完成验证 |
| Thermo Scientific SampleManager | LIMS与LES/ELN/SDMS及仪器、企业系统集成 | 检验执行中记录设备/方法/原始文件/解析版本；数据采集与业务流程分层 | 601、604、620、1400–1402 | 假设能零成本接所有仪器，或只存最终报告不存来源 |
| STARLIMS Quality Manufacturing | 样品、工作流、追溯、电子签名及制造质量流程 | 按岗位组织待办与异常；配置化审批、报告与状态控制 | 500、700–806、2000–2106 | 一次开发所有行业模板和无限制低代码平台 |
| 创腾制药实施案例 | 公开案例描述LIMS+LES+QMS及ERP协同 | 借鉴国内制药请验—执行—审核—ERP回传边界与中文操作习惯 | 201、601、806、1210 | 将实施方案误认为已核验的独立底层产品或照抄客户数据 |
| SENAITE（开源对照） | 样品/分析/工作表/仪器/报告，复核、状态与API | 参考样品/检验对象拆分、工作表组织和状态转换守卫 | 400–505、700–708 | 未做GMP差距与许可证评估就直接fork作为正式制药系统 |

## 转成自己的设计

LIMS负责样品和结果生命周期；LES思路负责按批准方法执行和约束步骤；ELN负责受控电子记录；SDMS思路负责原始文件及其来源。初期这些是同一应用中的模块，而非四个必须独立购买或拆分的系统。

先做三类可验收能力：1）同一批样品跨请验/取样/接收/检验/报告保持同一追溯链；2）方法、公式、标准和流程版本变更不影响历史记录；3）异常、资质、资源与职责隔离能真正阻断错误操作。沿用已接受V3.1，不为模仿竞品改掉已确认导航。

## 后续演示/PoC统一题目

请厂商或自研团队用相同合成样例展示：标准换版后旧样品复算；原始不合格结果及复测关系；跨实验室列表/附件/导出越权拒绝；两人同时扣减试剂及双人确认；批准后报告重印追溯；备份恢复后一致性。记录实际操作与证据，而不是只看PPT勾选表。

成本比较需分别询问授权（注册/并发/模块/站点）、实施、数据迁移、设备连接、验证、培训、升级、年度维护和退出导出；本轮没有可靠报价，不编造价格或自研省钱比例。

## 可核查来源（访问2026-11-16）

- LabWare Pharmaceutical：https://www.labware.com/industries/pharmaceutical
- LabVantage Pharma：https://www.labvantage.com/industries/pharma-biotech/
- LabVantage平台：https://www.labvantage.com/informatics/lims/
- Thermo SampleManager：https://www.thermofisher.com/us/en/home/digital-solutions/lab-informatics/lab-information-management-systems-lims/solutions/samplemanager.html
- STARLIMS：https://www.starlims.com/rd-quality-manufacturing-informatics-platform/lims/
- 创腾科伦实施案例：https://www.neotrident.com/cases/details/60.html
- SENAITE官方：https://www.senaite.com/

不复制厂商专有源码、界面资源或内部文档；开源参考需要逐组件核查许可与维护成本。
