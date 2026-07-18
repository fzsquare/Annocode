# Annocode

**Version 1.1.0**

Annocode 是一套面向 Codex 的干净上下文多 Agent 编程工作流。它将复杂需求拆分为规划、源码标注、实现、集成、测试和验收等独立职能，并要求每个职能在新的 Agent 上下文中执行。

主 Agent 只负责编排。各职能 Agent 不共享长聊天历史，而是通过 Annocode 工作区中的 Markdown 文件传递需求、任务契约、实现结果和验证证据。Planner 和 Annotator 完成后，流程会强制暂停，由主 Agent 向用户展示结构化总结，并在取得明确人工确认后才进入下一阶段。

## 概览

### 核心目标

- 隔离不同职能的上下文，减少长上下文污染。
- 让规划、实现、测试和验收保持职责独立。
- 支持主 Agent 自动创建职能子 Agent。
- 在 Planner 和 Annotator 完成后设置强制人工确认门禁。
- 将用户的批准、修改请求或拒绝按阶段和 attempt 写入追加式审计日志。
- 支持用户在独立 Codex 任务中手动创建职能 Agent。
- 通过 Requirement-ID 连接不同线程和 Agent。
- 通过文件交接保存可审查、可恢复的工程状态。
- 通过任务写入范围和依赖波次降低并行修改冲突。
- 只有独立验收 Agent 可以给出最终需求结论。

### Annocode 命名空间

| 对象 | 名称 |
|---|---|
| Skill 前缀 | annocode-* |
| 运行状态根目录 | .annocode/ |
| 需求工作区 | .annocode/requirements/<requirement-id>/ |
| 需求注册表 | .annocode/REGISTRY.md |
| 源码待实现标注 | ANNOCODE-CHANGE[...] |
| 源码已实现标注 | ANNOCODE-CHANGE-IMPLEMENTED[...] |

### 职能 Skills

| Skill | 职能 | 上下文 |
|---|---|---|
| annocode-feature-orchestrator | 初始化需求、调度角色、展示 Planner/Annotator 总结、记录用户确认、安排返工并向用户汇报 | 主 Agent |
| annocode-change-planner | 分析需求与代码库，生成验收标准、影响范围、任务 DAG 和文件所有权 | 独立 Planner Agent |
| annocode-source-annotator | 将任务映射到准确源码位置，并在验收后清理临时标注 | 独立 Annotator Agent |
| annocode-task-implementer | 完成一个任务和一次 attempt 的代码及测试代码 | 独立 Implementer Agent |
| annocode-integration-coordinator | 检查实现交接、跨任务契约、修改范围和测试候选 | 独立 Integration Agent |
| annocode-test-runner | 独立运行测试、构建和必要回归，记录可复现证据 | 独立 Test Runner Agent |
| annocode-acceptance-reviewer | 根据原始需求、验收标准、集成摘要和测试证据完成最终验收 | 独立 Acceptance Agent |

### 工作原则

#### 主 Agent 只负责编排

Orchestrator 可以初始化工作区、保存原始需求、创建职能 Agent、读取 handoff 状态、调度 Implementer、创建返工 attempt，并根据独立验收结论向用户汇报。

Orchestrator 不执行规划、源码标注、业务实现、正式测试或需求验收。

#### 每个职能使用新的 Agent

自动创建职能 Agent 时，只传递最小 Assignment Envelope：

~~~yaml
requirement_id: feature-example
role: implementer
task_id: T002
attempt: A1
~~~

子 Agent 不继承主聊天历史，而是从需求工作区读取自己的角色输入。

#### 文件是唯一交接通道

角色之间传递简洁的决策、契约、证据、风险和阻塞，不传递长聊天记录或隐藏推理过程。

#### Planner 和 Annotator 必须由用户授权

Planner handoff 达到 `COMPLETE` 后，Orchestrator 必须展示需求理解、验收标准、任务 DAG、文件所有权、风险和开放决策，并将状态设为 `WAITING_FOR_PLANNER_APPROVAL`。只有用户明确确认当前 Planner attempt，才允许创建 Annotator。

Annotator handoff 达到 `COMPLETE` 后，Orchestrator 必须展示任务标注覆盖、文件与符号、豁免项、阻塞和 Implementer 输入，并将状态设为 `WAITING_FOR_ANNOTATOR_APPROVAL`。只有用户明确确认当前 Annotator attempt，才允许创建 Implementer。

确认与具体阶段和 attempt 绑定。沉默、无关回复、已知晓角色完成或先前 attempt 的确认都不能授权下一阶段。用户要求修改时，必须创建新的职能 attempt，并在新结果完成后重新总结和确认。

## 架构与执行流程

### 执行架构

~~~mermaid
flowchart TD
    U["用户提交 Requirement-ID 和需求"] --> O["Orchestrator 主 Agent"]
    O --> P["新 Planner Agent"]
    P --> PH["Planner Handoff COMPLETE"]
    PH --> PS["Orchestrator 展示 Planner 总结"]
    PS --> PC{"用户确认 Planner attempt？"}
    PC -->|"要求修改"| P2["新 Planner attempt"]
    P2 --> PH
    PC -->|"明确确认"| PA["记录 Planner 审批"]
    PA --> A["新 Annotator Agent"]
    A --> AH["Annotator Handoff COMPLETE"]
    AH --> AS["Orchestrator 展示 Annotator 总结"]
    AS --> AC{"用户确认 Annotator attempt？"}
    AC -->|"要求修改"| A2["新 Annotator attempt"]
    A2 --> AH
    AC -->|"明确确认"| AA["记录 Annotator 审批"]
    AA --> I1["新 Implementer T001/A1"]
    AA --> I2["新 Implementer T002/A1"]
    AA --> I3["新 Implementer T003/A1"]
    I1 --> IH["Implementer Handoffs"]
    I2 --> IH
    I3 --> IH
    IH --> G["新 Integration Agent"]
    G --> GH["Integration Handoff"]
    GH --> T["新 Test Runner Agent"]
    T --> TH["Test Handoff"]
    TH --> R["新 Acceptance Agent"]
    R --> D{"验收结论"}
    D -->|"PASS"| C["新 Annotator Agent 清理标注"]
    D -->|"FAIL"| W["Orchestrator 创建新 attempt"]
    W --> I1
    D -->|"BLOCKED"| Q["请求用户决策"]
    C --> F["Orchestrator 最终汇报"]
~~~

### 执行时序图

~~~mermaid
sequenceDiagram
    actor User as 用户
    participant O as Orchestrator
    participant P as Planner Agent
    participant A as Annotator Agent
    participant I as Implementer Agent(s)
    participant G as Integration Agent
    participant T as Test Runner Agent
    participant R as Acceptance Agent

    User->>O: Requirement-ID + 需求 + 必要约束
    O->>O: 初始化工作区并保存原始需求
    O->>P: requirement_id + role=planner + attempt=A1
    P-->>O: Planner Handoff COMPLETE
    O-->>User: Planner 结构化总结 + 明确确认请求

    alt 用户要求修改
        User->>O: 修改意见
        O->>P: 新 Planner attempt
        P-->>O: 新 Planner Handoff
        O-->>User: 新总结 + 再次确认请求
    else 用户明确确认
        User->>O: 确认 Planner attempt
        O->>O: 追加 USER-APPROVALS.md
    end

    O->>A: requirement_id + role=annotator + attempt=A1
    A-->>O: Annotator Handoff COMPLETE
    O-->>User: Annotator 结构化总结 + 明确确认请求

    alt 用户要求修改
        User->>O: 补充或修正标注要求
        O->>A: 新 Annotator attempt
        A-->>O: 新 Annotator Handoff
        O-->>User: 新总结 + 再次确认请求
    else 用户明确确认
        User->>O: 确认 Annotator attempt
        O->>O: 追加 USER-APPROVALS.md
    end

    par 独立任务可并行
        O->>I: T001 + A1
        O->>I: T002 + A1
        O->>I: T003 + A1
    end
    I-->>O: Implementer Handoffs

    O->>G: role=integration
    G-->>O: Integration Handoff
    O->>T: role=tester
    T-->>O: Test Handoff
    O->>R: role=acceptance
    R-->>O: PASS / FAIL / BLOCKED

    alt PASS
        O->>A: cleanup mode
        A-->>O: 标注清理完成
        O-->>User: 实现结果、测试证据和剩余风险
    else FAIL
        O->>I: 新任务 attempt
    else BLOCKED
        O-->>User: 请求产品或工程决策
    end
~~~

### Requirement-ID

每个需求必须由用户指定稳定标识，例如：

~~~text
user-profile-cache
payment-retry
issue-1234
~~~

格式要求：

~~~text
[a-z][a-z0-9-]{2,63}
~~~

Requirement-ID 必须在当前仓库中唯一、创建后保持不变、不包含路径或敏感信息，并在自动和手动 Agent 调用中使用同一字符串。

完整 Agent 身份为：

~~~text
Requirement-ID + Role + Task-ID（如适用）+ Attempt
~~~

例如：

~~~text
user-profile-cache / implementer / T002 / A1
~~~

## 安装

### 环境要求

- Python 3.9 或更高版本。
- 支持 Skills 的 Codex 环境。
- 自动调度模式需要可创建独立子 Agent 的 Codex 环境。
- 手动模式需要多个能够访问同一仓库的 Codex 任务。

### 安装方式

克隆或下载本仓库后，在仓库根目录执行。

#### 安装到指定项目

~~~powershell
python .\install.py --project <目标项目目录>
~~~

Skills 将安装到：

~~~text
<目标项目目录>/.agents/skills/
~~~

#### 安装到当前用户

~~~powershell
python .\install.py --user
~~~

Skills 将安装到：

~~~text
~/.agents/skills/
~~~

#### 更新安装

~~~powershell
python .\install.py --project <目标项目目录> --force
~~~

或：

~~~powershell
python .\install.py --user --force
~~~

安装完成后重启 Codex，使其重新加载 Skills。

#### 手动安装

也可以将 skills/ 中的七个 Skill 目录复制到项目级或用户级 .agents/skills/。

## 使用指南

### 快速开始

#### 开始新需求

~~~text
使用 $annocode-feature-orchestrator 开始需求。

需求标识：user-profile-cache

需求：
为用户资料查询增加 5 分钟缓存。用户修改资料或权限变化时缓存必须立即失效，
保持现有 API 响应格式兼容，并增加必要的测试和指标。
~~~

#### 必需的人工确认

Planner 完成后，Orchestrator 会展示规划总结并暂停。用户可以确认当前 attempt：

~~~text
确认 Planner A1，可以进入源码标注阶段。
~~~

也可以提出修改：

~~~text
暂不确认。请增加缓存容量上限，并把降级行为加入验收标准。
~~~

Annotator 完成后，Orchestrator 会再次展示源码覆盖总结并暂停：

~~~text
确认 Annotator A1，可以开始实现。
~~~

只有这两次确认均已绑定到对应 attempt 并写入审批日志，Implementer 才能启动。

#### 继续需求

~~~text
使用 $annocode-feature-orchestrator 继续需求 user-profile-cache。
~~~

Orchestrator 会读取最新 handoff 和 `USER-APPROVALS.md`，判断应展示总结、等待确认还是创建下一职能。已有 handoff 不能代替用户确认。

### 手动创建职能 Agent

#### Planner

~~~text
使用 $annocode-change-planner 处理需求 user-profile-cache。
~~~

#### Annotator

~~~text
使用 $annocode-source-annotator 处理需求 user-profile-cache。
~~~

#### Implementer

~~~text
使用 $annocode-task-implementer 处理需求 user-profile-cache 的任务 T002。
~~~

#### Integration

~~~text
使用 $annocode-integration-coordinator 处理需求 user-profile-cache。
~~~

#### Test Runner

~~~text
使用 $annocode-test-runner 测试需求 user-profile-cache。
~~~

#### Acceptance Reviewer

~~~text
使用 $annocode-acceptance-reviewer 验收需求 user-profile-cache。
~~~

职能 Agent 完成后，回到主任务继续：

~~~text
使用 $annocode-feature-orchestrator 继续需求 user-profile-cache。
~~~

手动运行 Planner 或 Annotator 也不能跳过人工确认。Orchestrator 仍会先展示对应总结，并等待用户明确批准该 attempt。

### Implementer 并行执行

Planner 为每个任务生成稳定 Task-ID，并定义目标、依赖、Read set、Write set、接口契约、验收标准映射和测试代码要求。

只有依赖已满足且 Write set 不冲突的任务才能并行。手动并行时，为每个任务创建独立 Codex 任务：

~~~text
使用 $annocode-task-implementer 处理需求 user-profile-cache 的任务 T002。
~~~

~~~text
使用 $annocode-task-implementer 处理需求 user-profile-cache 的任务 T003。
~~~

## 工作区与质量闭环

### Annocode 工作区

每个需求的内部状态保存在：

~~~text
.annocode/requirements/<requirement-id>/
~~~

~~~text
.annocode/
├── REGISTRY.md
└── requirements/
    └── user-profile-cache/
        ├── README.md
        ├── MANIFEST.md
        ├── REQUEST.md
        ├── PROTOCOL.md
        ├── USER-APPROVALS.md
        ├── 10-plan.md
        ├── 20-task-board.md
        ├── 30-annotations.md
        ├── 40-integration.md
        ├── 50-test-report.md
        ├── 60-acceptance.md
        ├── 70-final.md
        ├── tasks/
        ├── handoffs/
        │   ├── 01-planner-to-annotator.md
        │   ├── 02-annotator-to-orchestrator.md
        │   ├── implementers/
        │   ├── 03-integration-to-test.md
        │   ├── 04-test-to-acceptance.md
        │   ├── 05-acceptance-to-orchestrator.md
        │   └── rework/
        └── artifacts/
~~~

用户通常不需要直接编辑这些文件。它们是职能 Agent 之间的持久通信协议。

### 人工确认审计

`USER-APPROVALS.md` 是 Orchestrator 所有的追加式审计日志。每条记录包含阶段、attempt、UTC 时间、用户原始决定文本、决定类型和被授权的下一角色。

支持的决定包括：

- `APPROVED`：批准当前 attempt，可以进入下一阶段；
- `REVISION_REQUESTED`：要求修改，创建同职能的新 attempt；
- `REJECTED`：拒绝当前方案，不授权下一阶段。

旧记录不得覆盖或删除。Planner 的确认只能授权 Annotator，Annotator 的确认只能授权 Implementer；确认不能跨 attempt 复用。

### 源码标注

Annotator 在准确源码位置插入短生命周期标注：

~~~typescript
// ANNOCODE-CHANGE[user-profile-cache/T002]
// intent: 对已授权的用户资料查询增加缓存
// accept: 缓存命中时不查询数据库，缓存故障时安全降级
~~~

Implementer 完成后更新为：

~~~typescript
// ANNOCODE-CHANGE-IMPLEMENTED[user-profile-cache/T002]
~~~

独立验收通过后，由新的 Annotator Agent 清理临时标注。具有长期维护价值的内容应改写为普通设计注释。

### 测试与验收

Test Runner 负责定向测试、单元测试、集成测试、lint、typecheck、build、风险回归以及命令和退出码记录。它不修改代码或断言，也不作业务验收。

Acceptance Reviewer 负责对照原始需求、检查验收标准完整性、关联代码与测试证据、检查非目标和约束，并给出 PASS、FAIL 或 BLOCKED。

只有 Acceptance Reviewer 的 PASS 可以作为需求完成依据。

### 返工机制

失败工作使用新的 Agent 和 attempt：

~~~text
T002 / Implementer / A1 -> FAIL
T002 / Implementer / A2 -> REWORK
~~~

返工 handoff 说明失败原因、复现证据、允许修改范围、新 attempt 和必须补充的完成证据。

如果返工被路由到 Planner 或 Annotator，新 attempt 完成后必须再次向用户展示总结并取得人工确认。实现层面的 Implementer 返工默认按任务路由，不重复要求 Planner 或 Annotator 确认，除非计划或源码覆盖范围发生变化。

### 完成条件

一个需求只有在以下条件全部满足时才完成：

- 原始需求已保存。
- Planner handoff 为 COMPLETE。
- `USER-APPROVALS.md` 中存在对应 Planner attempt 的 `APPROVED` 记录。
- Annotator handoff 为 COMPLETE。
- `USER-APPROVALS.md` 中存在对应 Annotator attempt 的 `APPROVED` 记录。
- 所有必需 Implementer 任务具有 READY_FOR_INTEGRATION handoff。
- Integration handoff 为 READY_FOR_TEST。
- Test handoff 为 TESTS_COMPLETE。
- Acceptance verdict 为 PASS。
- 临时 ANNOCODE-CHANGE 标注已清理。
- Orchestrator 已生成最终用户摘要。

### 完整交互示例

仓库根目录的 [example.md](./example.md) 使用“按筛选条件导出评论 CSV”需求，逐步展示用户输入、Planner/Annotator 强制确认、内部文件交接、Implementer 执行、测试、验收、返工和最终审计结果。

## 工具与项目集成

### 辅助脚本

#### 初始化需求工作区

~~~powershell
python .\skills\annocode-feature-orchestrator\scripts\init_annocode_requirement.py user-profile-cache --root <目标项目目录> --title "用户资料缓存" --request-file <需求文本文件>
~~~

#### 扫描源码标注

~~~powershell
python .\skills\annocode-source-annotator\scripts\scan_annocode_markers.py --root <目标项目目录> --requirement user-profile-cache
~~~

#### 验证工作区

~~~powershell
python .\skills\annocode-integration-coordinator\scripts\validate_annocode_requirement.py --repo-root <目标项目目录> --requirement user-profile-cache --phase init
~~~

phase 可选值为 init、plan 和 final。

### 项目结构

~~~text
.
├── .gitignore
├── README.md
├── example.md
├── VERSION
├── install.py
├── skills/
│   ├── annocode-feature-orchestrator/
│   ├── annocode-change-planner/
│   ├── annocode-source-annotator/
│   ├── annocode-task-implementer/
│   ├── annocode-integration-coordinator/
│   ├── annocode-test-runner/
│   └── annocode-acceptance-reviewer/
└── templates/
    └── AGENTS.md.snippet
~~~

### 项目级持久规则

可以将 templates/AGENTS.md.snippet 的内容合并到目标项目根目录 AGENTS.md，使 Codex 在复杂需求中遵守 Requirement-ID、干净上下文、独立职能 Agent 和文件交接规则。

## 版本

当前版本：**1.1.0**

### 1.1.0

- Planner 完成后强制展示结构化总结并等待用户确认。
- Annotator 完成后强制展示源码覆盖总结并等待用户确认。
- 新增按阶段和 attempt 记录决定的 `USER-APPROVALS.md` 追加式审计日志。
- 新增 [example.md](./example.md)，展示完整人机交互、内部交接、返工和验收过程。
