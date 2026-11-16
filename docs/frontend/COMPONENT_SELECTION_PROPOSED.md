# RFC-FE-002：HB-Lims React/Next.js 组件选型评估

- 状态：Proposed，不是已安装依赖或最终采购
- 范围：UI框架、数据表格、实验室数据输入、电子记录、报告、趋势、验证
- 基线：V3.1已采用视觉与交互；不因库切换就修改外观/业务流程

## 1. 设计系统选择

| 候选 | 强项 | 适合HB-Lims的地方 | 成本/风险 | 结论 |
| --- | --- | --- | --- | --- |
| Ant Design React v6 | 大量企业级表格/表单/弹窗/抽屉/树/选择控件，主题token | 请验/分配/样品列表、普通检验表单、管理台账与审批视图 | 需定制V3.1视觉；App Router需Registry/客户端边界 | **默认优先** |
| @ant-design/pro-components v3 | ProTable、ProForm、ProDescriptions等现成后台页面模板 | 主数据配置、物料/仪器台账等常规CRUD | 逐组件验证版本，勿使用不兼容v2拆分包；关键受控操作需额外显式设计 | **选择性使用** |
| shadcn/ui + Tailwind + Radix/Base UI | 可自定义组件源码及外观，适合强品牌与独特交互 | 高级化UI、特殊工作台布局 | 表单和复杂表格需要更多自研封装/维护/可访问性测试；与AntD同时全局铺开会造成冲突 | **替代方案，不作为默认第二套** |
| MUI + MUI X | Material风格成熟，Data Grid/日期/图表生态 | 数值密集与复杂数据网格 | MUI X Pro/Premium高级功能商业授权，V3.1视觉定制成本 | 备选 |

建议只固定**一个主UI系统**：AntD React (v6)+主题token+必要自建V3.1外壳。不建议全站 AntD/shadcn/MUI 三套混用。特种组件可以局部使用并隔离主题。

## 2. 按LIMS业务推荐组件

| 场景 | 首选 | 适用规则 |
| --- | --- | --- |
| 导航、台账、列表、状态 | AntD Table/ProTable、Menu、Tabs、Descriptions | 服务端分页和数据范围；绝不信任前端隐藏按钮等于权限 |
| 请验、取样、分配、标准配置 | AntD Form/ProForm + 清晰错误/焦点管理 | 表单的“提交”与“签署”是不同服务端命令 |
| 可编辑结果、复杂工作表 | AG Grid Community做PoC；TanStack Table为高度自定义备选 | 高级分组、Excel Export、Server-Side Row Model等需查企业许可，业务主数据不应只在客户端 |
| 批量选择、受控审批 | AntD Modal/Drawer/Steps + 自建签名核验流程 | 电子签名由后端进行再鉴别、版本和审计绑定，Modal不是签名系统 |
| 环境监测/稳定性趋势 | Apache ECharts | 趋势图由可追溯的后端数据产生，阈值/判定与版本明确 |
| 厂区/实验室点位图 | SVG图纸交互起步；必要时局部Canvas | 点位ID、区域状态、校准版本与结果记录由API提供 |
| 报告/检验记录预览 | 后端归档PDF + 受控PDF预览器 | 预览与实际签署的报告版本一致；打印请求与设备回执有别 |
| 服务器数据获取 | TanStack Query（必要时） | 保留后端权威数据；签署/审核时重新拉取对象版本 |
| 轻量交互状态 | React hooks / Zustand按需 | 不存全量样品/签名权威数据或持久密码/令牌 |
| 图标与品牌 | @ant-design/icons 或项目自有一套 | 图标/版权检查，品牌素材仅使用获许可版本 |
| 端到端验收 | Playwright + 视觉回归 + 可访问性工具 | 关键路径必须有真实执行证据；禁止Mock PASS冒充正式后端测试 |

若选择**shadcn/ui**作为主系统，则替代组合优先：shadcn/ui+TanStack Table+React Hook Form+Zod；所有可编辑输入都需要项目团队验证焦点、错误提示、ARIA、键盘、窄屏、受控提交和测试可复现性。它不是“即装即有的完整LIMS企业组件库”。

**混用限制：** 可在AntD主系统中局部引入AG Grid或ECharts；每种控件都要统一品牌Token、字体/间距、禁用/错误/加载/权限态和键盘行为。不要让ProTable、AG Grid、TanStack Table在同一类型的普通表格上三套并存。

## 3. 特别注意组件与许可证

- AntD v6要求React >=18及现代浏览器（非IE），图标包需同代；须验证Next/App Router CSS-in-JS SSR，AntdRegistry是官方方案。
- ProComponents v3在AntD v6上使用单体 @ant-design/pro-components；旧 @ant-design/pro-table 等v2子包不应混装。
- AG Grid Community可免费用于生产；Enterprise高级服务端行模型、透视、原生Excel导出等需要商业许可。MUI X社区版与Pro/Premium也不同许可。
- 不因浏览器组件默认显示“签署成功”“打印成功”而当作设备或后端确认；必须保留真实回执和失败证据。
- 当前独立GitHub仓库是Public，禁止引入实际检验结果、现场图纸敏感数据、内网凭据及商业代码未获授权版本。

## 4. PoC优先考察的五个页面

1. 我的工作：已采用V3.1风格、组件token和负责人待办。
2. 请验/样品台账：筛选、分页、详情、窄屏和权限拒绝。
3. 检验结果录入：小数、修约、标准快照、退回、刷新和并发冲突。
4. 审核/签名：职责隔离、再认证失败、双签与审计证据。
5. 检验报告：后端已归档版本预览/打印与来源追溯。

## 官方参考（查阅2026-11-16）

- https://ant.design/components/overview/ ; https://ant.design/docs/react/migration-v6/
- https://ant.design/docs/react/use-with-next/
- https://pro-components.antdigital.dev/docs/migration-guide.html
- https://ui.shadcn.com/docs/components/radix/data-table
- https://www.ag-grid.com/react-data-grid/community-vs-enterprise/
- https://mui.com/x/introduction/licensing/
- https://tanstack.com/query/latest/docs/framework/react/overview
- https://echarts.apache.org/en/
- https://playwright.dev/docs/intro
