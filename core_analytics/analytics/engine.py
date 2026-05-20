from core_analytics.agents.autonomous_analyst import autonomous_analyst_instance

class AnalyticsEngine:
    def __init__(self):
        self.analyst = autonomous_analyst_instance

    async def run(self, user_query: str):
        # The autonomous analyst handles the ReAct loop directly
        return await self.analyst.run(user_query)

analytics_engine = AnalyticsEngine()
