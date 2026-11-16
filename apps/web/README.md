# LIMS Web 开发分区

当前规范：[前端V2](../../docs/LIMS独立前端开发规范.md)、[FE-V1](../../docs/standards/FRONTEND.md)。采用React + Next.js App Router + TypeScript、AntD及Registry、TanStack Query、AntD Form/Table、nuqs；Recharts为图表主库，Zod/Zustand按需。

保留V3.1视觉，不使用新默认后台主题。源码计划按src/app、src/features、src/shared组织，路由/BFF不承担质量业务裁决。前端访问独立FastAPI，不直写质量库；不共享HBOS会话或质量数据库。

本目录尚无可运行应用或锁文件。首个工程PR须交精确依赖、主题token、OpenAPI客户端、合成Mock、五个代表页面和真实构建/浏览器证据。审批等关键写入不允许乐观成功，URL与缓存不得泄密。Vue/Vite/ProComponents/AG Grid不再是默认并列实现任务。
