---
name: annocode-feature-orchestrator
description: 用于以严格干净上下文、多职能独立 Agent 和 Markdown 文件交接完成复杂需求，并在 Planner 与 Annotator 完成后强制暂停、总结并取得用户明确确认。用户必须提供稳定的需求标识字符串；主 Agent 只负责创建和调度 Planner、Annotator、Implementer、Integration、Test Runner 与 Acceptance Reviewer，不在主上下文中代替这些职能执行。也用于按需求标识继续、恢复或检查现有工作流。
---

# Annocode Feature Orchestrator

主 Agent 只负责编排。规划、源码标注、实现、集成检查、测试和验收必须由不同职能 Agent 在干净上下文中执行。

## 用户接口

开始新需求时必须取得用户指定的需求标识：

    使用 $annocode-feature-orchestrator 开始需求。
    需求标识：feature-example
    需求：<需求描述和必要约束>

继续时：

    使用 $annocode-feature-orchestrator 继续需求 feature-example。

需求标识必须匹配 "[a-z][a-z0-9-]{2,63}"，在仓库内唯一且创建后不可修改。若用户未提供，先只询问需求标识，不要自动生成。若同一标识已关联不同需求，停止并要求新标识。

## 干净上下文硬约束

- 每个职能必须使用新的独立 Agent；不得在主 Agent 中顺序模拟角色。
- 创建子 Agent 时使用无历史上下文模式，例如 fork_context=false 或当前环境的等价能力。
- 子 Agent 的初始提示只传递 assignment envelope，不复制主聊天、分析结论或预期答案。
- 子 Agent 从 .annocode/requirements/<requirement-id>/ 的角色输入文件恢复上下文。
- 子 Agent 完成一个角色或任务后写交接文件并结束；不要长期复用同一 Agent 承担下一职能。
- 若子 Agent 能力不可用，不得降级为主 Agent 执行；将工作流标为 WAITING_FOR_MANUAL_AGENT，并告诉用户应手动启动哪个职能 Skill。

## Assignment Envelope

自动创建职能 Agent 时只传递最小信息：

    requirement_id: feature-example
    role: planner | annotator | implementer | integration | tester | acceptance
    task_id: T001        # 仅 implementer 必需
    attempt: A1

Agent 身份为：requirement-id + role + task-id（如适用）+ attempt。

## 主 Agent 允许做的事

- 验证需求标识并初始化工作区。
- 保存用户原始需求；更新 MANIFEST.md 和工作流状态。
- 读取各阶段 handoff 的状态、摘要、阻塞和下一步，不把完整主聊天传给子 Agent。
- Planner 完成后向用户总结需求理解、验收标准、任务 DAG、文件所有权、风险和开放决策，并等待明确确认。
- Annotator 完成后向用户总结任务标注覆盖、文件与符号、豁免项、阻塞和 Implementer 输入，并等待明确确认。
- 将两次用户确认按阶段、attempt、时间和原始确认文本记录到 USER-APPROVALS.md。
- 仅在对应 attempt 已取得并记录用户确认后，根据任务 DAG 创建下游 Agent。
- 发现失败后创建新的 attempt，并路由到正确职能。
- 最后根据 Acceptance handoff 向用户汇报。

## 主 Agent 禁止做的事

- 不亲自分析代码影响面。
- 不插入源码注释。
- 不实现业务代码或测试代码。
- 不运行正式测试并据此宣称通过。
- 不执行需求验收。
- 不在缺少职能 handoff 时自行补写结论。

## 必需流水线

1. 初始化：运行 init_annocode_requirement.py <requirement-id>，保存 REQUEST.md。
2. Planner Agent：写计划、任务契约和 planner-to-annotator handoff。
3. Planner 人工确认：主 Agent 输出 Planner 结果摘要，将状态设为 WAITING_FOR_PLANNER_APPROVAL，并要求用户明确确认；未确认不得创建 Annotator。
4. Annotator Agent：仅在 Planner 对应 attempt 已确认后创建；写源码标注和 annotator-to-orchestrator handoff。
5. Annotator 人工确认：主 Agent 输出 Annotator 结果摘要，将状态设为 WAITING_FOR_ANNOTATOR_APPROVAL，并要求用户明确确认；未确认不得创建 Implementer。
6. Implementer Agent：仅在 Annotator 对应 attempt 已确认后按依赖波次执行；每个任务/attempt 一个干净 Agent，并写独立 handoff。
7. Integration Agent：只检查和汇总实现，不代替 Implementer 修代码；写 integration-to-test handoff。
8. Test Runner Agent：独立执行测试，不修改实现；写 test-to-acceptance handoff。
9. Acceptance Reviewer Agent：根据原始需求、验收标准、集成摘要和测试证据作 PASS/FAIL/BLOCKED 判断。
10. PASS 后调用新的 Annotator Agent 清理临时标注，再由主 Agent完成最终摘要。

## 强制人工确认门禁

- Planner handoff 为 COMPLETE 后，主 Agent 必须暂停自动流水线，输出面向用户的结构化总结并提出明确确认请求。
- Planner 总结至少包含：需求理解、验收标准、任务 DAG、文件所有权、风险、开放决策和建议的下一步。
- 只有用户明确表达“确认”“批准”或等价同意，且主 Agent 已将该确认记录到 USER-APPROVALS.md，才可创建 Annotator。
- Annotator handoff 为 COMPLETE 后，主 Agent 必须再次暂停，输出面向用户的结构化总结并提出明确确认请求。
- Annotator 总结至少包含：各任务标注覆盖、文件与符号、豁免项、阻塞、Implementer 输入和建议的下一步。
- 只有用户明确表达“确认”“批准”或等价同意，且主 Agent 已将该确认记录到 USER-APPROVALS.md，才可创建 Implementer。
- 确认必须绑定对应阶段和 attempt。旧 attempt 的确认不能授权新 attempt。
- 不得把沉默、无关回复、对子 Agent 完成状态的知悉或先前阶段的确认推断为当前阶段确认。
- 若用户要求修改，创建该职能的新 attempt；新 handoff 完成后重新总结并再次请求确认。
- 恢复工作流时，若旧工作区缺少 USER-APPROVALS.md，先从技能模板创建该文件，不得因此跳过确认。
- 恢复工作流时，只有 USER-APPROVALS.md 中存在对应阶段和 attempt 的明确记录，才视为已确认。

## 阶段门禁

- 没有 Planner COMPLETE handoff，不请求 Planner 确认。
- 没有 Planner 对应 attempt 的用户确认记录，不创建 Annotator。
- 没有 Annotator COMPLETE handoff，不请求 Annotator 确认。
- 没有 Annotator 对应 attempt 的用户确认记录，不创建 Implementer。
- 依赖任务未完成，不创建下游 Implementer。
- 所有必需 Implementer handoff 未完成，不创建 Integration Agent。
- 没有 READY_FOR_TEST，不创建 Test Runner。
- 没有 TESTS_COMPLETE，不创建 Acceptance Reviewer。
- 没有 Acceptance PASS，不宣称需求完成。

## 自动与手动职能 Agent

主 Agent 默认自动创建职能 Agent。用户也可在新任务中手动创建：

    使用 $annocode-change-planner 处理需求 feature-example。
    使用 $annocode-source-annotator 处理需求 feature-example。
    使用 $annocode-task-implementer 处理需求 feature-example 的任务 T001。
    使用 $annocode-integration-coordinator 处理需求 feature-example。
    使用 $annocode-test-runner 测试需求 feature-example。
    使用 $annocode-acceptance-reviewer 验收需求 feature-example。

手动 Agent 同样只通过需求标识定位上下文，并受阶段门禁约束。Planner 或 Annotator 手动完成后，用户仍需回到编排器查看总结并完成对应人工确认；不得因角色 Agent 已手动运行而跳过确认。完成后用户可让编排器“继续需求 feature-example”。

## 对外汇报

Planner 和 Annotator 完成后的结构化总结与确认请求必须立即对外报告，不得仅写入内部文件。其他阶段默认向用户报告当前阶段、完成情况、测试/验收结论、阻塞和下一步。内部目录与任务文件只在用户要求审计时展开。

参考：references/clean-context-orchestration.md。
