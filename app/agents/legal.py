from app.agents.base_domain_agent import BaseDomainAgent

# Specialized Domain Agents
class LawyerAgent(BaseDomainAgent):
    def __init__(self):
        super().__init__("legal")