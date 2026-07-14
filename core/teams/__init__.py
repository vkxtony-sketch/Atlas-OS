"""Atlas OS - teams.

Groups of agents organised by responsibility. The Executive consults the
``TeamRegistry`` when ``ATLAS_USE_TEAMS`` is true (default true once
the package is imported).
"""

from core.teams.registry import TeamRegistry, list_teams
from core.teams.architecture_team import ArchitectureTeam
from core.teams.backend_team import BackendTeam
from core.teams.frontend_team import FrontendTeam
from core.teams.security_team import SecurityTeam
from core.teams.performance_team import PerformanceTeam
from core.teams.documentation_team import DocumentationTeam
from core.teams.testing_team import TestingTeam
from core.teams.research_team import ResearchTeam

# Register the eight teams declared by the Atlas OS spec.
TeamRegistry.register("architecture", ArchitectureTeam())
TeamRegistry.register("backend", BackendTeam())
TeamRegistry.register("frontend", FrontendTeam())
TeamRegistry.register("security", SecurityTeam())
TeamRegistry.register("performance", PerformanceTeam())
TeamRegistry.register("documentation", DocumentationTeam())
TeamRegistry.register("testing", TestingTeam())
TeamRegistry.register("research", ResearchTeam())

__all__ = ["TeamRegistry", "list_teams"]
