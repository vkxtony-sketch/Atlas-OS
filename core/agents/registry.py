"""Atlas OS - agent registry.

Single source of truth mapping agent role names → concrete classes.
The team registry and the Executive consult this.
"""
from __future__ import annotations

from typing import Any, Dict, List, Type

# Eager-import the canonical 12 agent roles so the registry is populated.

# Imported lazily by callers; importing here would create a cycle.
from core.agents.planner import PlannerAgent
from core.agents.coder import CoderAgent
from core.agents.critic import CriticAgent
from core.agents.researcher import ResearchAgent
from core.agents.code_reviewer import CodeReviewerAgent
from core.agents.security_reviewer import SecurityReviewerAgent
from core.agents.performance_reviewer import PerformanceReviewerAgent
from core.agents.documentation_writer import DocumentationWriterAgent
from core.agents.qa_engineer import QAEngineerAgent
from core.agents.knowledge import KnowledgeAgent
from core.agents.memory_agent import MemoryAgent
from core.agents.git_agent import GitAgent
from core.agents.deployment import DeploymentAgent
from core.agents.terminal import TerminalAgent
from core.agents.file_agent import FileAgent


AGENT_REGISTRY: Dict[str, Type] = {
    "planner": PlannerAgent,
    "coder": CoderAgent,
    "critic": CriticAgent,
    "researcher": ResearchAgent,
    "code_reviewer": CodeReviewerAgent,
    "security_reviewer": SecurityReviewerAgent,
    "performance_reviewer": PerformanceReviewerAgent,
    "documentation_writer": DocumentationWriterAgent,
    "qa_engineer": QAEngineerAgent,
    "knowledge": KnowledgeAgent,
    "memory": MemoryAgent,
    "git": GitAgent,
    "deployment": DeploymentAgent,
    "terminal": TerminalAgent,
    "file": FileAgent,
    "browser": None,  # registered by integrations hub when present
}


def register_agent(name: str, cls: Type) -> None:
    AGENT_REGISTRY[name] = cls


def get_agent(name: str) -> Type:
    cls = AGENT_REGISTRY.get(name)
    if cls is None:
        raise KeyError(f"Agent '{name}' is not registered in AGENT_REGISTRY.")
    return cls


def list_agents() -> List[str]:
    return sorted(AGENT_REGISTRY.keys())


def role_capabilities() -> Dict[str, List[str]]:
    """Friendly summary of what each agent role advertises."""
    return {
        "planner": ["decompose goal", "write plan", "track dependencies"],
        "coder": ["generate code", "improve code", "refactor code"],
        "critic": ["score output", "verify correctness"],
        "researcher": ["search", "summarise", "cite"],
        "code_reviewer": ["static review", "style enforcement", "smell detection"],
        "security_reviewer": ["vulnerability scan", "secret detection"],
        "performance_reviewer": ["complexity review", "memory profile stub"],
        "documentation_writer": ["API docs", "READMEs", "inline comments"],
        "qa_engineer": ["test plan", "edge cases", "regression list"],
        "knowledge": ["index documents", "semantic search stub", "tf-idf search"],
        "memory": ["short-term recall", "long-term store", "preferences"],
        "git": ["stage changes", "branch", "commit (with permission)", "PR prep"],
        "deployment": ["build", "container hint", "release notes"],
        "terminal": ["shell exec (with permission)", "diagnostics"],
        "file": ["list", "search", "rename", "bulk ops"],
        "browser": ["navigate", "fetch", "compare sources"],
    }
