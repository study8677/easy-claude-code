"""
Layer 7 — 三层权限系统
对应源码：claudecode_src/src/tools/BashTool/bashPermissions.ts
         claudecode_src/src/tools/BashTool/bashSecurity.ts

核心问题：Claude Code 怎么决定一条命令是否可以执行？

答：三道防线，从快到慢依次检查——

  第一层：语义拒绝（最快，静态分析）
    通过 tree-sitter AST 或字符串规则检测真正危险的操作。
    共 23 个检查器，每个都有数字 ID（方便遥测，避免字符串开销）。
    检测到危险 → 直接拒绝，不问用户。

  第二层：权限规则（用户定义的白名单/黑名单）
    用户可以配置：允许 `git commit:*`、禁止 `npm publish:*`。
    前缀匹配（npm run:*）或精确匹配。
    有规则命中 → 直接放行或拒绝，不弹提示。

  第三层：询问用户（最慢，兜底）
    前两层都没命中 → 弹出确认提示。
    同时智能建议一条规则，方便用户下次直接放行。

这个设计保证了：危险操作永远被拦截，安全操作不打扰用户。

无需 API Key 即可运行。
"""

import re
import shlex

# ─────────────────────────────────────────────────────────────
# 安全检查 ID（对应 bashSecurity.ts 的 BASH_SECURITY_CHECK_IDS）
# 用数字而非字符串：方便遥测统计，不浪费 token 序列化命令内容
# ─────────────────────────────────────────────────────────────
class SecurityCheckId:
    INCOMPLETE_COMMAND = 1
    OBFUSCATED_FLAGS = 4
    SHELL_METACHARACTERS = 5
    DANGEROUS_REDIRECT = 6
    COMMAND_SUBSTITUTION_INJECT = 8
    FORK_BOMB = 10
    DANGEROUS_ZSH_MODULE = 20
    HEREDOC_INJECTION = 21

@dataclass_helper = None  # 用普通类实现

class SecurityResult:
    def __init__(self, allowed: bool, check_id: int | None = None, reason: str = ""):
        self.allowed = allowed
        self.check_id = check_id
        self.reason = reason

    def __repr__(self):
        if self.allowed:
            return "✓ 通过"
        return f"✗ 拒绝 [检查器#{self.check_id}]: {self.reason}"


# ─────────────────────────────────────────────────────────────
# 第一层：语义安全检查（对应 bashSecurity.ts 的 checkBashSecurity()）
#
# 关键设计：每个检查器独立、有编号、fail-fast（第一个命中就返回）。
# 真实代码有 23 个检查器；这里实现最有代表性的 7 个。
# ─────────────────────────────────────────────────────────────
DANGEROUS_RM_PATTERNS = [
    r'\brm\s+(-[a-zA-Z]*f[a-zA-Z]*|-rf?|--force)\s+/',
    r'\brm\s+(-[a-zA-Z]*r[a-zA-Z]*)\s+[~/$]',
]

FORK_BOMB_PATTERN = r':\s*\(\s*\)\s*\{[^}]*:\s*\|[^}]*:\s*&'

DANGEROUS_ZSH_MODULES = {"zmodload", "sysread", "ztcp", "zsocket"}

def check_semantic_security(command: str) -> SecurityResult:
    """
    第一层：静态分析，检测真正危险的操作。
    注意：ZSH 危险模块被拦截，即使 Claude Code 本身不执行 ZSH——
    这是防御未来变化的"深度防御"策略。
    """

    # 检查器 #10：fork bomb（:(){:|:&};:）
    if re.search(FORK_BOMB_PATTERN, command):
        return SecurityResult(False, SecurityCheckId.FORK_BOMB, "fork bomb 模式")

    # 检查器 #6：危险重定向（覆盖系统文件）
    if re.search(r'>\s*/etc/|>\s*/proc/|>\s*/sys/', command):
        return SecurityResult(False, SecurityCheckId.DANGEROUS_REDIRECT, "写入系统目录")

    # 检查器 #20：危险 ZSH 模块
    tokens = set(re.findall(r'\b\w+\b', command))
    for module in DANGEROUS_ZSH_MODULES:
        if module in tokens:
            return SecurityResult(False, SecurityCheckId.DANGEROUS_ZSH_MODULE, f"危险 ZSH 模块: {module}")

    # 检查器 #4：混淆 flag（--fo\rce 等 unicode 欺骗）
    if re.search(r'--\w*\\[rn]\w*', command):
        return SecurityResult(False, SecurityCheckId.OBFUSCATED_FLAGS, "混淆 flag")

    # 检查器 #1：不完整命令（以管道/&&/|| 结尾）
    stripped = command.strip()
    if stripped.endswith(('|', '&&', '||', ';', '\\')):
        return SecurityResult(False, SecurityCheckId.INCOMPLETE_COMMAND, "命令不完整")

    # 危险 rm 模式（非强制拦截，但会触发警告）
    for pattern in DANGEROUS_RM_PATTERNS:
        if re.search(pattern, command):
            return SecurityResult(False, SecurityCheckId.DANGEROUS_REDIRECT,
                                  "递归删除系统路径，风险极高")

    return SecurityResult(True)   # 通过语义检查


# ─────────────────────────────────────────────────────────────
# 第二层：权限规则（对应 bashPermissions.ts 的 getCommandPermission()）
#
# 规则格式：Bash(前缀:*)  或  Bash(精确命令)
# 执行前会去掉环境变量：NODE_ENV=prod npm run build → 匹配 "npm run:*"
# ─────────────────────────────────────────────────────────────
class PermissionRule:
    def __init__(self, pattern: str, allow: bool):
        """
        pattern 示例：
          "git commit:*"  → 允许所有 git commit 命令
          "npm publish"   → 只允许精确的 npm publish（无参数）
          "rm:*"          → 允许所有 rm 命令（危险！）
        """
        self.allow = allow
        if pattern.endswith(":*"):
            self.prefix = pattern[:-2]
            self.exact = None
        else:
            self.prefix = None
            self.exact = pattern

    def matches(self, command: str) -> bool:
        # 先去掉 KEY=VAL 环境变量前缀（和真实代码行为一致）
        cmd = re.sub(r'^\s*(\w+=\S+\s+)+', '', command).strip()

        if self.prefix is not None:
            return cmd.startswith(self.prefix)
        else:
            return cmd == self.exact


class PermissionSystem:
    def __init__(self):
        self.rules: list[PermissionRule] = []

    def add_rule(self, pattern: str, allow: bool):
        self.rules.append(PermissionRule(pattern, allow))
        mode = "允许" if allow else "禁止"
        print(f"  [规则] {mode}: {pattern}")

    def check_rules(self, command: str) -> bool | None:
        """
        返回 True（允许）/ False（拒绝）/ None（无匹配规则，进入第三层）
        """
        for rule in self.rules:
            if rule.matches(command):
                return rule.allow
        return None   # 没有规则命中


# ─────────────────────────────────────────────────────────────
# 第三层：询问用户（对应 bashPermissions.ts 的 askPermission()）
#
# 关键设计：同时生成一条建议规则，方便用户下次不再被打扰
# ─────────────────────────────────────────────────────────────
def suggest_rule(command: str) -> str:
    """
    根据命令生成建议的白名单规则。
    真实代码会分析命令的"语义前缀"（e.g., git commit → git commit:*）
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()

    if not tokens:
        return command

    # 取前两个 token 作为前缀（git commit → "git commit:*"）
    if len(tokens) >= 2 and not tokens[1].startswith("-"):
        prefix = f"{tokens[0]} {tokens[1]}"
    else:
        prefix = tokens[0]

    return f"{prefix}:*"


def ask_user_permission(command: str) -> bool:
    """第三层：兜底询问"""
    suggestion = suggest_rule(command)
    print(f"\n  [权限确认] 即将执行:")
    print(f"    {command}")
    print(f"  建议规则（下次自动放行）: {suggestion}")
    answer = input("  允许？[y/N] ").strip().lower()
    return answer == "y"


# ─────────────────────────────────────────────────────────────
# 完整权限检查流程（三层合并）
# ─────────────────────────────────────────────────────────────
def can_execute(command: str, permission_system: PermissionSystem) -> bool:
    """
    对应 bashPermissions.ts 的 canExecuteCommand()。
    三层顺序执行，前一层有结论就不进入下一层。
    """
    # ── 第一层：语义安全检查 ──
    result = check_semantic_security(command)
    if not result.allowed:
        print(f"  [语义拦截] {result}")
        return False

    # ── 第二层：权限规则 ──
    rule_result = permission_system.check_rules(command)
    if rule_result is not None:
        status = "✓ 规则放行" if rule_result else "✗ 规则拒绝"
        print(f"  [{status}] {command}")
        return rule_result

    # ── 第三层：询问用户 ──
    return ask_user_permission(command)


# ─────────────────────────────────────────────────────────────
# 演示
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("═══ Layer 7：三层权限系统演示 ═══\n")

    # 初始化权限系统，预设一些规则
    perm = PermissionSystem()
    perm.add_rule("git commit:*", allow=True)   # git commit 全放行
    perm.add_rule("git push:*",   allow=True)   # git push 全放行
    perm.add_rule("npm publish",  allow=False)  # 精确禁止 npm publish
    print()

    test_commands = [
        # 第一层拦截
        (":(){:|:&};:",              "fork bomb"),
        ("echo test > /etc/passwd",  "写入系统文件"),
        ("rm -rf /home",             "危险递归删除"),
        # 第二层规则
        ("git commit -m 'fix bug'",  "已授权的命令"),
        ("npm publish",              "已禁止的命令"),
        # 第三层询问（如果上面两层没命中）
        ("ls -la",                   "普通命令，规则中没有"),
    ]

    for cmd, desc in test_commands:
        print(f"命令: {cmd}  ({desc})")
        result = can_execute(cmd, perm)
        print(f"结果: {'✓ 执行' if result else '✗ 拒绝'}\n")
