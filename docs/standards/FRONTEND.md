# FE-V1 前端工程与组件规范

视觉及业务权威见 [前端规范V2](../LIMS独立前端开发规范.md)；本文件只补充实现。状态：开发规范待PR审查，尚无可启动应用。

## FE-01 路由与组件边界

采用 `apps/web/src/app/` App Router、TypeScript strict；路由目录只负责layout/page/loading/error及访问体验。业务组件归 `src/features/<domain>/`，公共UI、主题、API客户端、auth适配归 `src/shared/`。界面合同归 `packages/contracts/`。不把所有代码塞入根page或一个全局App对象。

需要事件、状态、浏览器API的组件置于client边界；无需给所有文件标记'use client'，也不把整个应用强制改为Client Component。AntD在客户端组件中使用，由根layout的AntdRegistry管理SSR样式；SSR、Provider次序、hydration和首屏闪烁必须实测。Next新版本可能将Middleware称为Proxy：它只做初步路由拦截，不承担完整授权。

BFF只负责受控会话、可信凭据转发和必要聚合；不得把签名、复核、计算或审计规则复制到Server Actions。Server Actions/Route Handlers自身也要校验身份/CSRF/请求，并调用FastAPI；禁止直接写数据库。

## FE-02 主设计系统及风格

AntD是组件能力，不是新的视觉模板。使用ConfigProvider/theme tokens和项目外壳继承V3.1：原品牌、玻璃顶栏、圆角侧栏、紫色按钮和选中态、字号层级、间距、报告双品牌页眉/签名卡、标签及关键文案保持。禁止套Ant Design Pro默认布局、移动业务入口、换品牌或大幅改变色彩。ProComponents/AG Grid不是首版默认依赖。

先从原HTML提取token和组件尺寸，再做“原型—React实现”同场景、同视口截图对比。截图环境固定浏览器/字体/时区/视口/合成数据，动态区域必须标记允许差异。重大差异须Owner业务批准，测试人员不能直接刷新快照吞掉差异。文档段落一致和ZIP哈希一致不等于像素一致；本轮视觉验收NOT_RUN。

## FE-03 表单、表格和图表

AntD Form为表单唯一状态源。Zod用于有需要的字段组合/输入边界，并映射错误到Form；后端Pydantic和领域规则仍重新验证。明确小数/单位/日期表示，不能让浏览器二进制浮点决定检验结果。自动回填、粘贴和批量输入同样留可确认的来源。草稿脏状态下后台刷新不得无声覆盖输入。

AntD Table为默认网格：服务端分页、范围过滤、排序白名单、稳定rowKey；跨页批量操作由后端逐对象鉴权，不把当前页全选当全部结果。虚拟化需实测编辑焦点、键盘、读屏、选择及长行；不能为性能漏掉未渲染行的校验。遇到需要专业工作表的真实限制才申请新组件。

图表统一Recharts。质控/趋势的原始点、时间、单位、方法版本、阈值及后端算法版本可查；不能直接用前端图表拟合结果作质量判定。大数据抽样不得隐藏异常点，截图不能代替原始数据。特殊统计算法另建金标准用例。

## FE-04 查询与写入

TanStack Query缓存按稳定用户/实验室/查询条件分区；禁止跨请求共用服务端QueryClient。注销/换身份清除缓存；私有响应、SSR/RSC及BFF使用明确private/no-store策略并测试后退、预取和多实例，不依赖框架默认。

**禁止乐观成功**：受控结果保存/更正、签名、审核、放行、库存扣减、样品交接必须收到服务端持久化确认后显示成功。超时显示“结果待确认”，用幂等键查询原命令结果，不能直接再次提交或显示失败后制造重复签名。乐观更新只限列宽、个人显示偏好等非质量状态，必须可回退。

Query重试与自动刷新按操作配置；写命令不采用无限自动重试。请求包含expected_version和幂等键，409冲突显示服务器新版本并由用户确认，不静默覆盖。Mock/HTTP使用相同合同；Mock只允许合成环境，生产构建/运行均禁止静默回退。

## FE-05 URL与本地状态

nuqs接入App Router适配器，仅保存page/pageSize、排序、非敏感枚举等白名单。参数类型、上限、非法值在服务端再检查。批号、结果、员工姓名、备注、认证token、签名凭证不写入query string，避免浏览器历史、Referer和日志泄露；需要可分享查询时使用服务端授权的短期查询ID。

Zustand仅管理临时展示状态，不复制服务端质量记录成为第二权威源。浏览器存储持久化只用于明确的合成Mock，不保存真实记录、密码、JWT或签名凭证；真实草稿持久化在后端受控记录中完成。

## FE-06 签名、文件与报告

签名Modal只采集用户意图和必要鉴别，不是电子签名系统；取消/错密/过期/重复/越权不改变质量状态。不得在analytics、前端日志、浏览器trace里记录签名密码。

附件通过后端授权上传/预览/下载接口，不提供公共bucket。已批准报告展示后端冻结版本，保留来源/签名/哈希；预览、归档、重印必须关联同一版本。浏览器print事件仅说明打印请求/对话框状态，不保证纸张实际输出。

## FE-07 目录与测试

```text
apps/web/src/
  app/                  # (auth)、(workspace)、page/layout/providers
  features/             # samples、testing、quality、resources等
  shared/ui/            # 通用控件及LIMS品牌外壳
  shared/design-tokens/ # V3.1映射；数值待提取并审查
  shared/api-client/    # OpenAPI生成类型/客户端及统一错误
  shared/auth/          # 会话适配，不自行发明角色体系
  shared/schemas/
packages/contracts/     # API、命令、状态和错误合同
tests/e2e/
tests/visual/
tests/accessibility/
```

上面是实现路径约定，不表示目录已有源码。Vitest/Testing Library测试同步client组件与逻辑，Playwright承担真实浏览器及需要实际Next运行时的测试；async Server Component不以不支持的单元测试冒充覆盖。型别/Lint、Mock与真实API、桌面/窄屏、键盘、视觉、错密、越权、冲突、缓存及打印失败均需独立报告。每项关联URS/风险/构建SHA和实际证据。
