from .models import AgentAction


class AgentOrchestrator:
    def next_action(self,state):
        if not state.stable:return AgentAction("request_more_preference_data","preference state is not stable")
        return AgentAction("retrieve_furniture","preference state is stable")
