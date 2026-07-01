"""Direct test that plainweave_seed.seed returns the {locator: req_id} map.

Drives seed() with a fake `pw` closure (no real plainweave) returning canned
envelopes for the calls seed makes; asserts the three justified req-ids come back.
"""

from tour import plainweave_seed
from tour.plainweave_seed import ADD_BOOK, CLI_MAIN, REGISTER, TOUR_MAIN


def _fake_pw():
    state = {"n": 0}
    surfaces = [
        {"locator": ADD_BOOK, "sei": "sei-a"},
        {"locator": REGISTER, "sei": "sei-r"},
        {"locator": CLI_MAIN, "sei": "sei-c"},
        {"locator": TOUR_MAIN, "sei": "sei-t"},
    ]

    def pw(args):
        if args[:2] == ["intent", "coverage"]:
            return {"justified": surfaces, "unjustified": []}
        if args[:2] == ["goal", "add"]:
            return {"id": "GOAL-1"}
        if args[:2] == ["req", "add"]:
            state["n"] += 1
            return {"id": f"REQ-{state['n']}"}
        return {}

    return pw


def _fake_pw_with_trace():
    # Like _fake_pw but also answers the `trace propose`/`trace accept` calls the
    # with_trace_links=True branch makes — the coverage leg (Task 3) calls
    # seed(..., with_trace_links=True), and the dossier_trace conjunct depends on this
    # branch, so it needs direct unit coverage (the leg test mocks `seed` wholesale).
    state = {"n": 0, "link": 0}
    surfaces = [
        {"locator": ADD_BOOK, "sei": "sei-a"},
        {"locator": REGISTER, "sei": "sei-r"},
        {"locator": CLI_MAIN, "sei": "sei-c"},
        {"locator": TOUR_MAIN, "sei": "sei-t"},
    ]

    def pw(args):
        if args[:2] == ["intent", "coverage"]:
            return {"justified": surfaces, "unjustified": []}
        if args[:2] == ["goal", "add"]:
            return {"id": "GOAL-1"}
        if args[:2] == ["req", "add"]:
            state["n"] += 1
            return {"id": f"REQ-{state['n']}"}
        if args[:2] == ["trace", "propose"]:
            state["link"] += 1
            return {"id": f"LINK-{state['link']}"}
        if args[:2] == ["trace", "accept"]:
            return {}
        return {}

    return pw


def test_seed_returns_locator_to_req_id_map(tmp_path):
    m = plainweave_seed.seed(_fake_pw(), root=tmp_path)
    # justify() is called for ADD_BOOK, CLI_MAIN, REGISTER in that order.
    assert m == {ADD_BOOK: "REQ-1", CLI_MAIN: "REQ-2", REGISTER: "REQ-3"}


def test_seed_returns_map_with_trace_links(tmp_path):
    # with_trace_links=True must drive the trace propose/accept branch without KeyError
    # and return the SAME {locator: req_id} map (trace links don't change the contract).
    m = plainweave_seed.seed(_fake_pw_with_trace(), with_trace_links=True, root=tmp_path)
    assert m == {ADD_BOOK: "REQ-1", CLI_MAIN: "REQ-2", REGISTER: "REQ-3"}
