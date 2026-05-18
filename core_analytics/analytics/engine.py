from core_analytics.agents.planner import planner_instance
from core_analytics.analytics.artifact_synthesizer import ArtifactSynthesizer

class AnalyticsEngine:
    def __init__(self):
        self.planner = planner_instance
        self.synthesizer = ArtifactSynthesizer()

    async def run(self, user_query: str):
        # 1. Planner Agent melakukan dekomposisi dan eksekusi paralel
        return await self.planner.decompose_and_execute(user_query)

analytics_engine = AnalyticsEngine()
