"""Atlas OS - agent package.

Exposes the canonical 12+ agent roles from the spec, each backed by a
concrete class. New agents register themselves via ``register_agent``.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Type

from core.agents.base import BaseAgent
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

from core.agents.registry import AGENT_REGISTRY, register_agent, get_agent

__all__ = [
    "BaseAgent",
    "PlannerAgent",
    "CoderAgent",
    "CriticAgent",
    "ResearchAgent",
    "CodeReviewerAgent",
    "SecurityReviewerAgent",
    "PerformanceReviewerAgent",
    "DocumentationWriterAgent",
    "QAEngineerAgent",
    "KnowledgeAgent",
    "MemoryAgent",
    "GitAgent",
    "DeploymentAgent",
    "TerminalAgent",
    "FileAgent",
    "AGENT_REGISTRY",
    "register_agent",
    "get_agent",
]
