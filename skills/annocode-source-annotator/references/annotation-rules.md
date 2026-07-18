# 源码标注规则

## 好标注
- 位于真实改动点附近，而非文件顶部。
- 指向一个 task-id。
- intent 描述行为，不描述具体代码拼写。
- accept 描述可观察结果。
- 不重复任务契约中的长篇背景。

## 示例

TypeScript:

    // ANNOCODE-CHANGE[checkout-retry/T002]
    // intent: 对可重试网关错误执行有上限的退避重试
    // accept: 最多重试 3 次，非重试错误立即返回

Python:

    # ANNOCODE-CHANGE[checkout-retry/T003]
    # intent: 记录最终失败的结构化指标
    # accept: 指标包含 provider 和 error_class，不包含敏感数据

SQL:

    -- ANNOCODE-CHANGE[checkout-retry/T001]
    -- intent: 保存幂等键和网关响应引用
    -- accept: 幂等键唯一，旧数据迁移安全

## 生命周期
ANNOTATED -> ANNOCODE-CHANGE-IMPLEMENTED -> 验证 PASS -> 删除临时标注。

如果普通维护者未来仍需了解原因，把内容改写为普通设计注释，并引用稳定的 ADR 或 issue，而不是保留 AI 流程标签。
