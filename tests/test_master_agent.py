from backend.agents.master_agent import master_agent_node


def test_master_agent_infers_molecule_and_indication() -> None:
    state = {"query": "metformin for breast cancer"}

    new_state = master_agent_node(state)

    assert new_state["molecule"] == "metformin"
    assert new_state["indication"] == "breast cancer"
    assert isinstance(new_state["query_plan"], list)
    assert new_state["master_confidence"] in {"low", "medium", "high"}
    assert isinstance(new_state["logs"], list)
    assert any(msg.startswith("[master]") for msg in new_state["logs"])


def test_master_agent_initializes_logs_when_missing() -> None:
    state = {"query": "oncology opportunities"}

    new_state = master_agent_node(state)

    assert isinstance(new_state["logs"], list)
    assert new_state["indication"] == "oncology"
