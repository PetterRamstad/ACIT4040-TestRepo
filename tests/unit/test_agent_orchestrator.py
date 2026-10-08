from packages.agents.orchestrator import AgentOrchestrator

def test_unstable_requests_more_data():
 class S: stable=False
 assert AgentOrchestrator().next_action(S()).name=='request_more_preference_data'

def test_stable_proceeds_to_retrieval():
 class S: stable=True
 assert AgentOrchestrator().next_action(S()).name=='retrieve_furniture'
