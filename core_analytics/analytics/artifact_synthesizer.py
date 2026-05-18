from typing import List
from core_analytics.agents.base import AgentArtifact

class ArtifactSynthesizer:
    def synthesize(self, artifacts: List[AgentArtifact]) -> str:
        summary = "Analytical Summary:\n"
        for art in artifacts:
            summary += f"- [{art.name}] {art.content}\n"
        return summary
