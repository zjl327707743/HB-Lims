# 独立前端开发分区

**2026-11-16 React/Next技术规范补充（仍为待审提案）：** [RFC-FE-001 前端技术实施规范](../../docs/frontend/REACT_NEXTJS_TECH_SPEC_PROPOSED.md) 与 [RFC-FE-002 组件选型对照](../../docs/frontend/COMPONENT_SELECTION_PROPOSED.md)。优先PoC Next App Router 与 React+Vite；不推翻原V3.1视觉规范、不把早期Vue建议视为定案。

**技术栈待选：** React/TypeScript/Ant Design、Vue3/TypeScript/Ant Design Vue、Angular/TypeScript并列评估；现有V3.1仅定义被采用的视觉/交互基线。见 [ADR-0002](../../docs/architecture/adr/0002-independent-validation-architecture-evaluation.md)。下方原Vue建议只是历史初始方案。

状态：仅分区与合同，尚未创建可启动应用。建议Vue3/TypeScript/Ant Design Vue，待ADR批准后在本目录创建并锁定工程依赖。

以原V3.1为交互和视觉依据；建议src下按features、components、commands、adapters、stores、router、styles、i18n组织。我的工作/请验/检验/复核/资源等按业务域划分，禁止继续往单个HTML追加覆盖脚本。

Mock与HTTP实现同一数据合同，Mock可重置、可持久化且版本化；页面不直接操作localStorage或调用任意业务URL。Mock身份不是正式权限，生产不得静默回退Mock。

验收需桌面/窄屏、键盘、报告预览/打印、完整业务及拒绝路径；未做实际浏览器回归不得标通过。关联Issue #4。
