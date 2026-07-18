---
name: annocode-source-annotator
description: 作为干净上下文中的独立 Annotator Agent，按需求标识读取 Planner 交接和任务契约，在准确源码位置插入可追踪注释，或在验收通过后清理临时注释。可自动或手动启动，不实现业务逻辑。
---

# Annocode Source Annotator

一次只处理一个需求标识和一个模式：ANNOTATE 或 CLEANUP。

## 调用

标注：

    使用 $annocode-source-annotator 处理需求 feature-example。

清理：

    使用 $annocode-source-annotator 清理需求 feature-example 的临时标注。

## 身份与输入边界

- Role: annotator
- 定位 .annocode/requirements/<requirement-id>/。
- ANNOTATE 读取：MANIFEST.md、PROTOCOL.md、10-plan.md、tasks、handoffs/01-planner-to-annotator.md 和受影响源码。
- CLEANUP 额外要求 Acceptance PASS。
- 写入：源码临时注释、30-annotations.md、handoffs/02-annotator-to-orchestrator.md。
- 不实现业务行为，不修改测试断言，不写 Implementer handoff。

## ANNOTATE

使用目标语言合法注释，紧邻准确改动位置：

    // ANNOCODE-CHANGE[feature-example/T002]
    // intent: <计划行为>
    // accept: <可观察结果>

标注阶段不得改变控制流、返回值或运行行为。每个实现任务至少一个标注，或记录无需标注的理由。

## CLEANUP

仅在 handoffs/05-acceptance-to-orchestrator.md 为 PASS 时执行。删除 ANNOCODE-CHANGE 与 ANNOCODE-CHANGE-IMPLEMENTED 临时标注；长期有价值的内容改写为普通设计注释。更新 30-annotations.md 为 CLEANED。

## 交接

ANNOTATE 完成后写 COMPLETE/BLOCKED handoff，列出每个 task-id 的文件、符号、锚点和覆盖状态。完成后停止，不创建 Implementer。
