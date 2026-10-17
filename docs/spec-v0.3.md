# Judicious
## Architecture & Product Specification

**Version:** 0.3 Draft  
**Status:** Proposed — 待审阅  
**Category:** Agent Skills / Software Engineering  
**Tagline:** Engineering Judgment for AI Coding Agents

---

# 1. 产品定义

Judicious 是一套面向 AI Coding Agent 的工程判断能力，帮助 Agent 在开发、维护和重构长期演进的软件项目时，保持代码库的结构一致性、职责清晰性和可维护性。

它不取代编译器、Linter、Language Server 或 Agent Harness，而是为现有开发工具提供统一的工程判断原则、反模式识别方法和改进动作。

Judicious 必须能够：

- 独立安装和使用。
- 通过统一命令入口调用。
- 通过独立原子 Skills 被其他 Agent 组合和复用。
- 利用宿主已有的代码搜索、规划、审查和编辑功能。
- 在不安装额外 Runtime 的条件下完成核心工作。
- 根据实际验证结果，逐步增强分析和自动化能力。

## 1.1 核心原则

**Reuse Before Creation**

创建新实现之前，先发现并评估现有代码、标准库和依赖包提供的能力。

**Correct Placement Before Abstraction**

不仅判断代码是否需要存在，还要判断它应当位于哪个模块、Package、语言层或运行时。

**One Canonical Responsibility**

同一个领域职责应有明确的权威实现。避免长期维护语义重合的平行 API 和独立状态来源。

**Justified Complexity**

每一层抽象、间接调用、兼容机制和依赖，都应当有明确、可验证的存在理由。

**Evidence-Based Judgment**

重要的工程建议必须基于实际代码、调用关系、依赖契约或测试证据，而不是仅凭函数命名和通用经验。

**Native First**

优先使用宿主 Agent 已有的 Skills、Plan Mode、Subagents、代码导航、编辑和测试能力。

**Composable by Design**

每项能力具有独立的职责和调用接口。组合不应依赖 Judicious 自己实现的任务编排器。

**Progressive Enhancement**

只有证明当前方案存在明确不足，才增加 AST、索引器、Hooks、CI 检测器或其他基础设施。

---

# 2. 命令 API

## 2.1 双入口设计

Judicious 同时提供统一入口和原子入口。

### A. 统一入口

遵循 Impeccable 的使用风格：

```text
/judicious <command> [target or instruction]
```

例如：

```text
/judicious init
/judicious audit
/judicious audit src/api
/judicious critique
/judicious distill src/services
/judicious placement normalize_matrix
/judicious polish
```

用户输入：

```text
/judicious
```

应显示可用命令、用途和简短示例。

如果用户直接提供自然语言任务，Judicious 可以依据任务意图选择对应能力；存在实质性歧义时，应说明选择或询问。

### B. 原子入口

每个核心能力也可以独立调用：

```text
/judicious:init
/judicious:audit
/judicious:reuse
/judicious:placement
/judicious:critique
/judicious:distill
/judicious:consolidate
/judicious:harden
/judicious:polish
```

两类入口必须具有一致的语义、检查要求、修改权限和输出标准。

例如：

```text
/judicious reuse create_project
```

与：

```text
/judicious:reuse create_project
```

应当执行相同的判断过程。

经 `npx skills add` 安装时，技能名就是命令名（`reuse`、`critique`），没有 `judicious:` 前缀。仓库按 `skills/<name>/SKILL.md` 发布，目录名等于 frontmatter 的 `name`。

**重要：** 这里定义的是目标公共 API。Claude Code Plugin 的原生命名空间可以承载原子命令；不带命名空间的 `/judicious` 入口需要通过宿主原生 Skill 安装或薄适配实现。必须实测对应宿主的命令解析行为，不能假设 Plugin 安装后会自动拥有两个入口。

## 2.2 命令分类

| 命令 | 职责 | 默认行为 |
|---|---|---|
| `init` | 初始化治理、全面审计、债务引导 | 审计并请求后续治理确认 |
| `audit` | 全局或指定范围的架构及技术债检查 | 只读 |
| `reuse` | 已有能力发现和复用判断 | 只读 |
| `placement` | 实现归属、提取与下沉判断 | 只读 |
| `critique` | 定向工程质量审查 | 只读 |
| `distill` | 精简冗余实现和复杂性 | 修改代码 |
| `consolidate` | 收敛重复职责和平行 API | 修改代码 |
| `harden` | 加固契约、架构边界和异常处理 | 修改代码 |
| `polish` | 提交前的综合检查与小范围清理 | 检查及有限修改 |

`init` 和 `audit` 必须能够独立调用。

除 `init` 外，所有命令都不应要求事先完成项目初始化。

## 2.3 参数设计

不建设专门的参数解析系统。

初期由 Claude 解释自然语言目标和简单命令参数。

例如：

```text
/judicious audit --changed
/judicious audit --focus duplication
/judicious critique src/core
/judicious reuse "parse configuration"
/judicious placement src/utils/parser.py
```

约定：

- 不提供 Target 时，以当前项目或当前变更为默认范围，具体由命令决定。
- 路径可以是文件、目录或 Workspace 内的 Package。
- 自然语言可以描述领域能力或架构问题。
- `--changed` 表示审查 Git 变更。
- `--focus` 表示优先审查某类问题，不代表忽略必要的相关证据。

这些是 Skill 的交互约定，不是独立 CLI 的参数协议。

---

# 3. 原子能力定义

## 3.1 Reuse

**问题：是否已经存在可满足需求的能力？**

检查顺序：

1. 当前文件和相邻模块。
2. 当前 Package 公开接口。
3. Workspace 内其他 Package。
4. 现有直接依赖和标准库。
5. 有充分线索时进一步扩展搜索。

主要决策：

- `REUSE`：直接使用已有实现。
- `COMPOSE`：组合现有能力。
- `EXTEND`：扩展已有接口。
- `REPLACE`：替换旧实现。
- `CREATE`：新增实现更合理。
- `UNRESOLVED`：证据不足。

必须评估语义一致性、公开契约、依赖方向、生命周期和维护成本。

禁止：

- 未搜索已有能力便新增公共 API。
- 因命名不同而重复实现已有功能。
- 无理由复制依赖包中的算法。
- 为调用已有 API 创建无实际职责的 Wrapper。
- 仅因表面相似而强制复用。

### 搜索预算

采用逐级扩展、证据驱动的搜索。

默认优先扫描当前 Package 和直接依赖，不递归遍历全部第三方源码。

允许依据可靠线索继续搜索，不设机械的三跳硬上限。

搜索终止时必须区分：

`FOUND`、`NOT_FOUND_IN_SCOPE` 和 `UNKNOWN`。

在有限范围内未找到，不能宣称能力在整个代码生态中不存在。

---

## 3.2 Placement

**问题：代码应该在哪里实现？**

支持五种主要决策：

- `KEEP`：保留当前实现位置。
- `MOVE`：移动到更合适的现有模块。
- `EXTRACT`：提取为可复用组件。
- `LOWER`：下沉到更底层的共享实现。
- `REMOVE`：删除不必要的实现。

其中 `LOWER` 是独立的重要判断能力。

### Lowering 检查

评估以下方面：

1. 功能是否具有独立的底层语义。
2. 是否存在真实的多个消费者。
3. 是否能够跨 Package 或运行时复用。
4. 下沉是否会引入上层业务依赖。
5. 是否涉及 ABI、FFI、WASM 或序列化成本。
6. 底层 API 是否会不必要地膨胀。
7. 测试、性能和部署方式是否受影响。
8. 是否存在比下沉更简单的复用路径。

例如，一个上层 Python 包中的通用算法被浏览器端同时需要时，Judicious 应评估是否适合提取到共享核心，并通过 Python Binding 和 WASM 暴露。

但它不得仅因为代码可以使用 Rust 重写，就建议迁移到 Rust。

### 否定性条件

发现以下情况时，默认不建议下沉：

- 实现依赖上层领域策略。
- 下沉会反转依赖方向。
- 不同消费者需要不同的语义。
- 跨语言边界成本大于实际复用收益。
- 共享需求尚未被证实。

下沉是架构决策，不是代码移动操作。

---

## 3.3 Critique

**问题：现有代码的工程设计哪里不合理？**

审查内容：

- 重复职责与平行实现。
- API 设计一致性。
- 模块边界与依赖方向。
- 抽象深度和间接层。
- 状态与 Schema 权威来源。
- 不必要的兼容逻辑。
- 实现位置与职责归属。
- 演进后的遗留代码。

Critique 必须优先报告结构性根因，而不是大量琐碎的代码风格问题。

其输出应明确：

- 问题是什么。
- 为什么是问题。
- 相关代码证据。
- 哪些例外可能使该设计合理。
- 建议的改进方向。
- 判断置信度与尚未验证的部分。

Critique 不修改代码。

---

## 3.4 Audit

**问题：整个代码库目前存在哪些架构问题和技术债？**

Audit 是全局审计能力，可以被用户独立调用，也可以被 Init 复用。

覆盖范围：

1. Duplication — 重复实现与平行 API。
2. Ownership — 职责分裂和权威实现不清晰。
3. Architecture — 错误依赖、跨层绕行及循环依赖。
4. Abstraction — 冗余 Wrapper 和不必要的通用化。
5. Placement — 不合理的模块归属及可下沉能力。
6. Evolution — 废弃实现、未完成迁移和兼容债务。
7. Contracts — API 不一致及高风险边界。

### 审计策略

先进行项目级探索，理解主要模块和依赖。

再定位高风险领域，执行针对性深度检查。

对具有相同根因的问题进行合并。

最后输出：

- 主要架构问题。
- 影响范围。
- 相关证据。
- 优先级及风险。
- 建议的治理动作。
- 尚未覆盖的区域。

Audit 必须诚实报告检查覆盖率。

不能因为运行了一轮有限搜索，就宣布整个代码库不存在重复实现。

Audit 永远只读。

---

## 3.5 Init

**问题：如何让现有项目建立良好的工程治理起点？**

Init 是薄编排入口，而不是独立的分析引擎。

流程：

```text
INIT
  │
  ├── Discover project conventions
  │
  ├── AUDIT
  │     ├── Existing implementations
  │     ├── Architecture
  │     ├── APIs
  │     └── Technical debt
  │
  ├── Triage findings
  │
  ├── Propose remediation priorities
  │
  ├── User-approved remediation
  │     └── Native Claude planning/editing
  │
  └── Re-audit and establish baseline
```

Init 必须调用与独立 Audit 命令相同的审计能力定义，不允许维护自己的审计逻辑。

如果宿主支持直接委托原子 Skill，则使用该机制；否则读取同一份权威 Audit 定义并执行，不通过复制 Prompt 模拟第二套实现。

### 技术债治理

Init 应当主动给出高优先级的债务治理建议。

用户确认后，可以使用宿主原生 Plan Mode、编辑和测试能力分批解决。

每批修改完成后重新审计受影响范围。

Init 不默认自动重构整个仓库。

不强制创建新的 Plan、Spec 或任务格式。

可以在用户确认后，将长期有效的架构约束写入项目现有的 `CLAUDE.md`、`AGENTS.md` 或既有架构文档。

当需要跨会话保留技术债基线、且项目没有合适的现有载体时，可以选择性保存轻量审计摘要。

不能把推测性的架构归属写成已经确认的项目规范。

---

## 3.6 Distill

**问题：哪些代码可以在保持行为的前提下被删除或简化？**

主要处理：

- 无实际职责的包装层。
- 多余的 Adapter。
- 假想的扩展点。
- 不必要的配置项。
- 无价值的间接调用。
- 重复的简单工具逻辑。
- 已不再使用的实现。

必须保留：

- 正确性。
- 必要的错误处理。
- 可观察行为。
- 公开契约。
- 实际存在的兼容要求。

删除不是目的，降低不必要的复杂性才是目的。

---

## 3.7 Consolidate

**问题：多个分散实现是否应当收敛为一个权威实现？**

步骤：

1. 找到所有相关实现。
2. 比较真实语义和行为契约。
3. 识别所有消费者。
4. 判断是否应该合并。
5. 选择权威实现。
6. 使用原生规划和编辑工具迁移调用方。
7. 删除旧实现。
8. 运行测试并重新检查。

如果消费者之间存在实质性语义差异，允许保留独立实现。

禁止为了消除表面重复而创建不合理的共享抽象。

---

## 3.8 Harden

**问题：已有架构和公共契约是否足够稳健？**

主要关注：

- 公共 API 的输入输出契约。
- 错误传播和异常边界。
- 资源生命周期。
- 明确的依赖方向。
- 关键不变量。
- 回归测试。
- 消费者兼容性。

优先强化现有实现，不因为 Harden 而发明新基础设施。

---

## 3.9 Polish

**问题：当前变更是否已经具备合并条件？**

Polish 是面向当前 Git Diff 的最终工程质量检查。

包括：

- 是否复用了已有能力。
- 是否增加重复实现。
- 新增代码是否位于正确模块。
- 是否产生新公共 API。
- 是否留下废弃实现。
- 是否引入不必要的复杂性。
- 是否完成相关测试与验证。

默认允许有限、低风险的局部修正。

涉及跨模块重构、公共 API 迁移或能力下沉时，应先形成方案并取得确认，不在 Polish 中顺手执行大型架构变更。

---

# 4. Skill 组合架构

## 4.1 核心约束

**一个工程判断，一份权威定义，多个调用入口。**

统一入口和原子入口不允许各自维护相似但略有差异的判断逻辑。

发布布局（skills.sh 与 `npx skills add` 认的就是这一棵）：

```text
judicious/
├── AGENTS.md                   钩子注不进去时的常驻复用卡片
├── INSTALL.md                  Claude、Grok、skills CLI 的安装与卸载
├── plugin.json                 Grok 插件名
├── skills.sh.json
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json        source 为 ./，钩子留在仓库根
├── .grok-plugin/
│   └── marketplace.json        source 为 ./
├── hooks/                      Claude 插件才安装；npx skills add 不带钩子
└── skills/
    ├── judicious/SKILL.md      统一入口
    ├── reuse/SKILL.md
    ├── placement/SKILL.md
    ├── critique/SKILL.md
    ├── audit/SKILL.md
    ├── init/SKILL.md
    ├── distill/SKILL.md
    ├── consolidate/SKILL.md
    ├── harden/SKILL.md
    └── polish/SKILL.md
```

每项能力的权威定义就是 `skills/<name>/SKILL.md`。目录名等于 frontmatter 的 `name`。共享原则写在该文件里，因为商店按单个 skill 目录安装，不会带上仓库里的其他文件。

统一入口根据意图调用同名 skill（`critique`、`reuse`，而不是 `judicious:critique`）。斜杠入口是 `judicious` 这个 skill。仓库不提供 `commands/` 目录。

`AGENTS.md` 收录与 Claude SessionStart 钩子相同的复用卡片。Grok 的 SessionStart 不能把说明注入会话，所以 Grok 安装靠这份文件。根目录 `plugin.json` 只写插件名，并把 `hooks` 置空，避免 Grok 加载仓库根的 Claude 钩子。`.grok-plugin/marketplace.json` 与 `.claude-plugin/marketplace.json` 的 `source` 都是 `./`，插件目录因此包含 `skills/`。

仓库根不能再放一份 `SKILL.md`，否则它会挡住 `skills/` 下面的全部技能。

不维护第二份手工同步的副本，也没有构建脚本。

## 4.2 运行模型

Judicious 不开发自己的：

- Agent Scheduler。
- Plan 管理器。
- Spec 管理器。
- 文件编辑引擎。
- 自定义 Subagent 通信协议。
- Agent 状态数据库。

需要规划时，使用宿主的原生规划能力。

需要隔离审查时，使用原生 Subagent。

需要文件修改时，使用原生编辑工具。

需要代码定位时，使用原生代码导航或已安装的分析工具。

需要审批时，使用宿主已有的权限及批准机制。

---

# 5. Evidence Hand-off

## 5.1 目的

支持原子 Skill 之间及外部 Agent 之间的证据复用，避免不必要的重复探索。

默认使用自然语言结论和代码引用。

只有跨上下文传递或复杂任务明确需要时，才生成紧凑的 Evidence Receipt。

## 5.2 最小证据内容

```yaml
capability: configuration-parsing
scope: src/config/
revision: abc123

decision: REUSE
canonical: src/config/parser.py:42

evidence:
  - Existing public function satisfies requirements
  - Tests cover expected behavior

disqualifiers_checked:
  - Semantic mismatch
  - Invalid dependency direction

unknown:
  - External dynamic consumers
```

该格式是参考结构，不建立正式 Schema Registry。

接收方需要检查代码证据是否仍然有效。

Receipt 不能代替必要的新增搜索，也不能被视为不可推翻的架构决定。

---

# 6. 反模式与否定性判断

Judicious 应维护统一的反模式知识库，重点描述 AI Coding Agent 常见的工程错误。

首版包括：

| 反模式 | 含义 |
|---|---|
| Parallel Implementation | 为相同职责创建第二套实现 |
| API Proliferation | 不断增加语义重合的公共接口 |
| Shallow Wrapper | 无独立职责的参数转发层 |
| Shadow State | 同一权威状态存在多个独立来源 |
| Speculative Generality | 为假设需求建立抽象 |
| Premature Extraction | 没有真实收益便提取共享模块 |
| Premature Lowering | 不合理地下沉业务逻辑 |
| Architecture Bypass | 为局部方便绕过模块边界 |
| Compatibility Accumulation | 无期限保留旧 API 和兼容层 |
| Dead Implementation | 替换后仍残留的旧实现 |

每个反模式描述：

- 典型症状。
- 为什么通常有害。
- 可能合理的例外。
- 应当检查哪些证据。
- 常见的改进方向。

不要求将任何反模式机械应用于所有代码库。

---

# 7. 自动调用与权限

## 7.1 自动发现

原子 Skill 应有精确的 `description`，帮助 Claude 在相关任务中自动选择。

例如：

`reuse` 适用于新增实现、寻找现有 API、依赖能力复用和避免重复逻辑。

`placement` 适用于模块职责、跨 Package 提取、共享核心和跨运行时下沉。

`critique` 适用于工程架构审查、重复实现与抽象质量分析。

自动调用是期望行为，不视为可靠性保证。

必须单独测试显式调用、自然语言自动触发和外部 Subagent 预加载。

## 7.2 权限边界

**只读能力：**

- Reuse
- Placement
- Critique
- Audit

只允许探索和分析代码。

**可修改能力：**

- Distill
- Consolidate
- Harden
- Polish

可根据任务目标修改代码，但必须验证结果。

**编排能力：**

- Init

默认执行只读审计。需要写入项目约束或修复技术债时，进入明确的用户批准步骤。

写入权限不仅通过 Prompt 约束，还应尽可能使用宿主原生权限机制执行。

---

# 8. 技术边界

## 8.1 首版不引入独立 Runtime

V0.1 只需要：

- Markdown Skills。
- 共享 Reference 文件。
- Claude Code 原生工具。
- 小型评测集。

不引入 Rust、AST、数据库、MCP Server 或常驻服务。

## 8.2 可选代码理解工具

后续如有必要，允许接入：

- Language Server。
- AST 结构分析。
- 精确符号索引。
- 依赖图分析。
- 外部 API / Package 搜索。
- 独立 Code Intelligence Provider。

工具的职责是提供更准确的代码证据。

Judicious 继续负责工程判断，不将自身判断逻辑写入特定索引器。

## 8.3 可组合性

外部 Agent 可以独立使用 `reuse` 或 `placement`，也可以提供自己的搜索与代码分析工具。

Judicious 不要求外部消费者采用其目录结构、任务格式或执行流程。

依赖方式应优先采用宿主支持的 Skill 引用、预加载和工具扩展机制。

---

# 9. 渐进式开发路线

每个阶段完成后，都必须证明该阶段带来了实际价值，才进入下一阶段。

## Stage 0 — Evaluation Baseline

准备小型评测集，覆盖：

- 正确复用已有 API。
- 拒绝语义不同的同名实现。
- 判断何时需要新增实现。
- 识别重复 API。
- 拒绝无价值的抽象。
- 容忍合理的少量重复代码。

记录无 Judicious 时 Agent 的行为。

**验收：** 评测案例能够真实地区分好的工程判断与坏的工程判断。

## Stage 1 — Skill MVP

实现：

- 统一入口 `/judicious` 的基础路由。
- `reuse`。
- `critique`。
- 对应原子入口。
- 最小反模式参考。
- 显式调用和基础自动触发测试。

不实现其他工具链。

**验收：** 与 Baseline 相比，正确复用率提高，重复实现减少，功能正确性不下降。两个入口的行为一致。

## Stage 2 — Comprehensive Audit

实现：

- `audit` 独立命令。
- 跨模块架构检查。
- 技术债分类。
- 根因归并。
- 覆盖范围说明。
- 只读审计报告。

不强制引入代码索引器。

**验收：** Audit 能发现局部 Critique 容易遗漏的全局问题，且结论有明确证据。

## Stage 3 — Init & Debt Remediation

实现：

- `init`。
- 内部复用 Audit。
- 技术债优先级判断。
- 原生用户审批和规划。
- 分批修复后的重新审计。
- 可选的长期约束与基线保存。

**验收：** 新项目不需要维护额外的 Judicious 流程文件即可完成初始化；已有项目可以实际减少一批已确认技术债。

## Stage 4 — Dependency Discovery & Placement

强化：

- 当前依赖能力发现。
- Workspace 公开 API 发现。
- 正确复用与错误复用的区分。
- Placement 五类决策。
- 跨 Package 和跨运行时的 Lowering 评估。

**验收：** Agent 能正确判断保留、提取和下沉，并能拒绝不合理的下沉建议。

## Stage 5 — Refinement Commands

实现：

- `distill`。
- `consolidate`。
- `harden`。
- `polish`。

复用已存在的判断规则，避免为每个命令重新建立分析体系。

**验收：** 重构前后功能保持一致，实际复杂性下降，无新架构违规。

## Stage 6 — Composition & Portability

验证：

- 统一入口与原子入口语义一致。
- 外部 Skill 能组合 Reuse 和 Placement。
- Subagent 能正确预加载 Judicious。
- 跨上下文 Evidence Hand-off。
- 不同宿主的安装和调用行为。

**验收：** 至少两种不同的宿主工作流能够复用 Judicious，不必复制其工程判断规则。

## Stage 7 — Optional Tooling

只有出现明确瓶颈时，才评估：

- AST / LSP 增强。
- 增量符号索引。
- Rust Code Intelligence。
- Lifecycle Hooks。
- 规则检测器。
- CI Integration。

每项技术必须单独证明收益。

**验收：** 新增基础设施能够解决已观测到的问题，其维护和执行成本与收益相称。

---

# 10. 质量与验收标准

## 10.1 行为质量

Judicious 应提高正确复用率，减少重复实现和无效抽象。

同时不得以牺牲正确性和模块独立性为代价追求代码减少。

## 10.2 调用一致性

统一命令和原子 Skill 使用相同的权威规则。

必须测试：

- 参数和目标范围一致。
- 修改权限一致。
- 证据要求一致。
- 结论分类一致。
- 相同测试场景下不存在系统性决策分歧。

允许模型输出措辞存在差异，不要求文字完全相同。

## 10.3 组合质量

被外部 Agent 调用时，Judicious 不应强制接管规划、工具选择或任务执行。

它应能够使用已有上下文和证据，输出可被宿主继续消费的判断。

## 10.4 上下文成本

Skill 应使用渐进式披露。

主入口保持精简，仅加载当前任务相关的命令与参考资料。

不要求全部反模式、代码示例和技术文档常驻上下文。

## 10.5 审计可靠性

每个重要 Finding 必须关联实际代码证据。

无法确认时必须明确说明不确定性。

不能将语义审查意见伪装成确定性的静态分析结果。

## 10.6 重构安全性

任何修改代码的能力，必须利用项目已有的测试、构建和静态检查机制验证结果。

无法执行测试时应明确报告，不得声称修改已被验证。

---

# 11. Non-Goals

Judicious 不计划成为：

- 新的 Coding Agent。
- 新的 Agent Harness。
- 新的 Plan / Spec 管理框架。
- 新的语言服务器。
- 新的编译器或 Linter。
- 通用代码搜索引擎。
- 自动迁移所有项目架构的重构平台。
- 强制所有开发者采用统一代码风格的规则系统。

它是工程判断能力，而不是替代现有开发基础设施的综合框架。

---

# 12. 首次实现范围

**0.1 交付全部九个命令。**

必须完成：

1. 统一入口 `/judicious`，以及九个原子命令：`init`、`audit`、`reuse`、`placement`、`critique`、`distill`、`consolidate`、`harden`、`polish`。
2. 单一权威命令定义和共享工程原则。统一入口委托原子 skill，不维护第二份判断逻辑。
3. 无 Runtime、无 AST、无 MCP、无 CI 检测器。Stage 7 的工具只有在测到明确瓶颈后才单独评估，不进入 0.1。

评测案例、fixture 和评测脚本不随仓库发布。Stage 0 的基线在开发中用过，不作为发布物保留。

目录和接口按第 4 节组织。后续能力加在同一套命令定义上，不另起一份。

---

# 13. 最终设计原则

Judicious 的目标不是让 Agent 尽可能少写代码，而是让 Agent **只编写有充分理由存在、处于正确位置、能够长期维护的代码**。

在功能设计上，应当首先复用宿主能力。

在架构设计上，应当首先寻找正确的职责归属。

在重构过程中，应当首先保护现有契约和行为。

在扩展 Judicious 自身时，同样遵循上述原则。

**Judicious should improve engineering judgment without becoming another engineering problem.**
