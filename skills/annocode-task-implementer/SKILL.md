---
name: annocode-task-implementer
description: 作为干净上下文中的独立 Implementer Agent，按用户指定的需求标识和任务编号读取最小任务契约、源码标注及依赖交接，完成限定范围的代码和测试代码，并发布独立实现 handoff。每个任务和每次返工使用新的 Agent。
---

# Annocode Task Implementer

一个 Agent 只处理一个 requirement-id、一个 task-id 和一个 attempt。

## 调用

    使用 $annocode-task-implementer 处理需求 feature-example 的任务 T002。

自动创建时由 Orchestrator 额外传递 attempt。手动调用未指定 task-id 时：若恰好一个任务 READY 且未分配，可选择它；若有多个，停止并列出可选 task-id，不自行争抢。

## 身份与输入边界

- Role: implementer
- 读取：MANIFEST.md、PROTOCOL.md、自己的 tasks/Txxx.md、handoffs/02-annotator-to-orchestrator.md、直接依赖任务的 Implementer handoff，以及任务 Read set。
- 不读取完整主聊天、其他无关任务 handoff 或其他需求目录。
- 写入：任务 Write set 中的代码/测试代码，以及 handoffs/implementers/<task-id>-<attempt>.md。
- 不修改任务看板、测试报告、验收报告或其他任务文件。

## 执行

1. 验证 requirement-id、task-id、attempt、阶段和依赖状态。
2. 确认 Write set 未被其他活动任务占用。
3. 按源码标注和任务契约做最小完整实现。
4. 添加任务所需测试代码；可以运行定向自检，但自检不是正式 Test Runner 结论。
5. 将自己的标注改为 ANNOCODE-CHANGE-IMPLEMENTED。
6. 写 READY_FOR_INTEGRATION、BLOCKED 或 REWORK_REQUIRED handoff。

## Handoff

必须包含身份、修改文件、公共接口/schema/配置变化、自检命令与结果、偏离计划、风险、下游依赖说明和建议状态。

完成后停止。不得承担 Integration、Tester 或 Acceptance 角色。

参考：references/implementer-handoff.md。
