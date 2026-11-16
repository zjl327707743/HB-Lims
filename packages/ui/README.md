# V3.1 共享界面能力

主系统为Ant Design React。继承V3.1品牌、玻璃顶栏、侧栏、紫色主操作、报告和标签，不套用另一套默认主题。详见 [FE-V1](../../docs/standards/FRONTEND.md)。

先在apps/web/src/shared提取token及通用组件，出现明确复用再迁入本包，避免提前建复杂设计系统。Form/Table是默认，其他库须ADR。语义错误/加载/权限/冲突、键盘和窄屏统一验收。

当前无已实现组件或经浏览器核验的token数值；文档保留条款不代表视觉回归完成。
