"""Deterministic subset of scoring-rules.md. Unsupported events remain unscored."""
RED = {"red", "sheriff"}
BLACK = {"mafia", "don"}

def calculate(roles, events):
    scores = {n: 0 for n in range(1,11)}
    entries = []
    pending = []
    for event in events:
        actor = event["actor"]
        targets = event["targets"]
        kind = event["kind"]
        a_role = roles.get(actor, "unknown")
        target_roles = [roles.get(t, "unknown") for t in targets]
        if a_role == "unknown" or "unknown" in target_roles:
            pending.append(event["id"])
            continue
        deltas = []
        if kind == "nomination":
            same = (a_role in RED) == (target_roles[0] in RED)
            deltas = [(actor, -3 if same else 3)]
        elif kind == "vote":
            if a_role in RED:
                target = target_roles[0]
                deltas = [(actor, -1 if target in RED else (3 if target == "don" else 2))]
            else:
                pending.append(event["id"])  # No black vote rule specified.
                continue
        elif kind == "will":
            if a_role in RED:
                for target, role in zip(targets, target_roles):
                    deltas.extend([(actor, 3 if role in BLACK else -3), (target, -1)])
        else:
            pending.append(event["id"])
            continue
        for seat, delta in deltas:
            scores[seat] += delta
            entries.append(dict(event_id=event["id"],seat=seat,delta=delta))
    return scores, entries, pending
