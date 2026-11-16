# RFC-FE-001：HB-Lims React / Next.js 前端技术补充规范

- 状态：**Proposed / 待Owner、技术负责人及QA评审，绝非最终选型**
- 日期：2026-11-16
- 对象：HB-Lims 独立前端，未来可能采用 React/Next.js；与后端框架、数据库选型解耦
- 原始权威：docs/LIMS独立前端开发规范.md 和根目录 LIMS_V3.1_已采用交付包.zip；URS维持原编号
- 相关架构：docs/architecture/adr/0002-independent-validation-architecture-evaluation.md

## 1. 固定要求与可选项

**固定：** V3.1 已采用的顶部品牌、玻璃顶栏、圆角导航、紫色主操作、我的工作、请验与取样、检验电子记录、审核批准、报告/标签、设备、稳定性、留样和环境监测的行为；服务端负责权威业务命令、权限、签名、审计及状态变化；按185条URS做追踪。禁止将旧 HTML 单页脚本直接扩展为生产系统。

**待选择：** React+Next.js App Router 对比 React+Vite+React Router/TanStack Router；Ant Design React 对比 shadcn/ui、MUI；特殊数据网格用 AG Grid/TanStack Table。所选的UI框架不得暗中改变已采用交互和验收要求。

## 2. Next.js 是否值得用

| 方案 | 主要适用情形 | 付出的代价 |
| --- | --- | --- |
| React + Next.js App Router（优先PoC候选） | 需要单独受控的Node Web服务、SSO/BFF、服务器组件或服务端首屏；愿意把Next纳入受控验证范围 | 多一套Node运行时、SSO代理/缓存/Server Action/构建和升级验证 |
| React + Vite SPA | 内部系统不需要SEO/SSR；API已有独立会话和登录方案，期望较小部署验证边界 | SSR/BFF需另设，复杂SSR和服务端能力不是内建 |
| Next.js static export | 仅在所有动态身份/数据都完全由独立API完成、无需Next服务端功能时考虑 | 不支持需Node服务端的身份/BFF/Server Actions/运行时动态能力 |

暂推荐在 PoC 中比较 Next Node Server 部署与 Vite 静态部署；不能因为React/Next热度或SEO概念就强选Next。若Next方案胜出：使用当前受支持、经过兼容性测试且已修补安全漏洞的Next 16.x/React 版本，锁依赖及Node镜像摘要；Next官方最低Node20.9并非建议长期固定最低版本。

## 3. 核心系统边界

- HBOS Portal只链接LIMS独立域名；若使用SSO，按实际协议由LIMS/受控BFF对接企业IdP。不能共享HBOS/Frappe数据库或session，也不能让前端角色切换代替真实授权。
- Next.js只做Web/渲染和必要BFF/会话处理；**核心质量业务API独立**（FastAPI、Spring Boot、ASP.NET Core均可）。Next Route Handlers/Server Actions不是LIMS签名/审计/批准/原始结果写入的权威业务层。
- 对业务操作如 submit、record-result、review、approve，统一调用 LIMS 后端显式命令；后端校验身份、角色、厂区/实验室/小组/任务范围、资质、状态、对象版本、原因、幂等键与签署再鉴别。
- 如果采用Next BFF：默认仅在受信任服务端持有OIDC令牌，使用Secure/HttpOnly/合适SameSite cookie与CSRF防御，不把会话密钥、签名密码或长期令牌放到localStorage；后端仍独立执行鉴权。
- 公共质量记录、已签署数据与个人结果禁止进入静态生成产物、共享缓存、跨用户复用的RSC缓存或浏览器持久化。私有数据动态请求须使用明确的非缓存策略（必要时 cache: 'no-store'、Cache-Control private/no-store），并测试预取、后退、重载、换身份和多实例时隔离有效；无缓存标志不是唯一安全措施。
- 生产对报告以已批准的后端版本化文件/PDF作为权威。浏览器预览显示已归档版本；打印操作记录“请求”和真实设备“完成回执”不能混同。审批和结果不应只依赖客户端计算。
- Next server/client边界：App Router page/layout可以为服务端组件，复杂可编辑表格、扫码、图纸交互、电子记录等使用独立 'use client' 组件；不在大量Client组件中导入本不需要的服务端逻辑。
- Next Node服务支持全功能；静态导出不能使用需要运行时服务器的行为。若使用AntD，在layout配置AntdRegistry，测试样式注入及首屏/水合；避免不兼容的点号子组件导入。
- 不启用默认公开API读写受控记录，不将授权决策只放在 Next proxy/middleware；任何直接访问LIMS API或BFF的路径均须测拒绝。

## 4. 目录提案（仅建议，不代表已创建应用）

```text
apps/web/
  app/
    layout.tsx
    providers.tsx
    (auth)/
    (workspace)/
      layout.tsx
      work/
      samples/
      testing/
      review/
      reports/
      resources/
      stability/
      retention/
      environment/
      settings/
  features/
    samples/{components,api,hooks,model,tests}/
    testing/{components,api,hooks,model,tests}/
    quality/{components,api,hooks,model,tests}/
    resources/{components,api,hooks,model,tests}/
    reporting/{components,api,hooks,model,tests}/
  shared/
    ui/
    design-tokens/
    api-client/
    auth/
    schemas/
    utilities/
  styles/
  public/          # 仅经许可公开的静态素材
packages/
  contracts/       # OpenAPI、错误码、状态、命令、版本
  ui/              # 仅证实复用后再提取
tests/
  e2e/
  accessibility/
  visual/
```

职责：app只做路由/布局/加载边界；features拥有业务可交互UI、视图模型与测试；shared保存经确认的公共能力；packages/contracts只定义经批准的前后端合同，不在前端重建审批规则。一个业务对象有一个服务端记录源。

## 5. 推荐前端依赖（候选，未执行安装）

- 基础：React + TypeScript + Next.js App Router（选择Next时）；Ant Design React v6 & @ant-design/icons 同代 + @ant-design/nextjs-registry；以 Design Tokens 继承V3.1而非强行使用antd默认主题。
- 页面模板：@ant-design/pro-components v3 的 ProTable/ProForm/ProDescriptions 等可用于标准台账和配置，须逐项验证 Next/AntD 版本。不要混装旧拆分@ant-design/pro-* v2包和v3单体包。
- 服务器状态：TanStack Query（客户端表格、轮询、数据失效）；用户交互小状态按需useState/Zustand，避免全仓唯一巨型App状态。批准后应以后端响应为准，任何乐观更新不得隐藏失败。
- 表单：如果使用AntD基础，先统一 AntD Form/ProForm，复杂重复行与可测试性不满足时再评估React Hook Form+Zod；不得在一个业务表单中并存两个互相冲突的校验/状态源。客户端校验仅为体验，服务端重新验证。
- 常规列表：Ant Design Table/ProTable；结果录入/多维大量数据视情况PoC AG Grid Community 或 TanStack Table。若要服务端行模型/高级分组/内建Excel导出等Enterprise能力，单独评估授权，不因功能存在就默认免费可用。
- 趋势：Apache ECharts，用于EM趋势、稳定性和仪器统计；界面图形不能替代权威计算与判定。
- 高级交互：点位图先用SVG支持缩放和点击，有真实复杂需求才引入画布/流程图等依赖。PDF预览可用受控浏览器内PDF渲染器，实际档案在后端。
- 验证：TypeScript strict、ESLint、单元/组件测试、Playwright真实浏览器E2E、可访问性及V3.1截图对照；关键步骤留版本、测试身份、预期与实际、失败证据。

## 6. 必须保持的V3.1视觉规则

- 保留玻璃拟态顶栏、圆角侧栏、紫色主操作、海滨/健康元已批准品牌、信息层级、“我的工作”、报告双品牌页眉、签名卡和标签布局。
- 不因为换Next/React就全面重做视觉。将原色彩、字号、间距、圆角、阴影、栅格、交互态逐项提取为token并做截图差异评审。
- 读写密集实验室页面优先清晰字体、对比度、表格密度与键盘操作，动画不能妨碍输入、失焦、审计确认或打印。
- 移动端/窄屏保证重要弹窗和表单可用；桌面应重点覆盖大型表格、签名、记录和报告。

## 7. PoC与进入实现的验收门槛

PoC须在同一V3.1示例和同一Mock/HTTP合同下比对React+Next与React+Vite：首屏/导航、复杂表格、长表单、弱网、操作延迟、权限拒绝、签名再认证、报告预览/打印、缓存隔离、SSO登录/失败、刷新恢复、浏览器回归。记录实际构建产物与运行环境、包体积、冷启动、测试路径、人员维护成本和第三方验证可复现性。不得造性能排名或在未建应用前宣布任一PoC PASS。

批量录入和报表须额外验证：小数精度、单位、修约、标准版本、字段可追溯；受控更正不能悄然修改服务器原始结果。电子签署不得只做Modal或复制用户姓名。

## 8. 官方资料（2026-11-16核查）

- Next App Router/Client组件：https://nextjs.org/docs/app/getting-started/server-and-client-components
- Next BFF能力/局限：https://nextjs.org/docs/app/guides/backend-for-frontend
- Next静态导出限制：https://nextjs.org/docs/app/guides/static-exports
- Next自托管/缓存和版本偏移：https://nextjs.org/docs/app/guides/self-hosting
- AntD v6：https://ant.design/docs/react/migration-v6/
- AntD Next集成：https://ant.design/docs/react/use-with-next/
- ProComponents v3：https://pro-components.antdigital.dev/docs/migration-guide.html
- AG Grid Community/Enterprise：https://www.ag-grid.com/react-data-grid/community-vs-enterprise/
- TanStack Query：https://tanstack.com/query/latest/docs/framework/react/overview
- Playwright：https://playwright.dev/docs/intro
