"""
automata_engine.py
Core engine for DFA and NFA simulation, epsilon-closure, and NFA-to-DFA conversion.
"""

from collections import defaultdict, deque
from typing import Dict, FrozenSet, List, Optional, Set, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# DFA
# ─────────────────────────────────────────────────────────────────────────────

class DFA:
    """
    Deterministic Finite Automaton  (Q, Σ, δ, q0, F)

    Parameters
    ----------
    states       : set of state labels
    alphabet     : set of symbols (strings)
    transitions  : dict  { (state, symbol): next_state }
    start_state  : initial state
    accept_states: set of accepting states
    """

    def __init__(
        self,
        states: Set,
        alphabet: Set[str],
        transitions: Dict[Tuple, object],
        start_state,
        accept_states: Set,
    ):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

    def run(self, input_string: str) -> Tuple[bool, List[dict]]:
        """
        Simulate the DFA on *input_string*.

        Returns
        -------
        accepted : bool
        trace    : list of step dicts for visualisation
        """
        current = self.start_state
        trace = [{"step": 0, "symbol": "START", "from": None, "to": current, "accepted": False}]

        for i, symbol in enumerate(input_string, start=1):
            key = (current, symbol)
            if key in self.transitions:
                next_state = self.transitions[key]
            else:
                # dead / trap state
                trace.append({
                    "step": i,
                    "symbol": symbol,
                    "from": current,
                    "to": "DEAD",
                    "accepted": False,
                })
                return False, trace

            trace.append({
                "step": i,
                "symbol": symbol,
                "from": current,
                "to": next_state,
                "accepted": next_state in self.accept_states,
            })
            current = next_state

        accepted = current in self.accept_states
        return accepted, trace

    def get_transitions_table(self) -> List[dict]:
        """Return transitions as a list of dicts (for display in a table)."""
        rows = []
        for (state, symbol), next_state in sorted(self.transitions.items(), key=str):
            rows.append({
                "Current State": state,
                "Input Symbol": symbol,
                "Next State": next_state,
                "Is Accept": next_state in self.accept_states,
            })
        return rows


# ─────────────────────────────────────────────────────────────────────────────
# NFA
# ─────────────────────────────────────────────────────────────────────────────

EPSILON = "ε"


class NFA:
    """
    Non-Deterministic Finite Automaton with ε-transitions.

    Parameters
    ----------
    states        : set of state labels
    alphabet      : set of symbols (not including ε)
    transitions   : dict  { (state, symbol_or_ε): set_of_next_states }
    start_state   : initial state
    accept_states : set of accepting states
    """

    def __init__(
        self,
        states: Set,
        alphabet: Set[str],
        transitions: Dict[Tuple, Set],
        start_state,
        accept_states: Set,
    ):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

    # ── ε-closure ─────────────────────────────────────────────────────────────

    def epsilon_closure(self, state_set: Set) -> FrozenSet:
        """Return ε-closure of a set of states."""
        closure = set(state_set)
        stack = list(state_set)
        while stack:
            s = stack.pop()
            for t in self.transitions.get((s, EPSILON), set()):
                if t not in closure:
                    closure.add(t)
                    stack.append(t)
        return frozenset(closure)

    def epsilon_closure_single(self, state) -> FrozenSet:
        return self.epsilon_closure({state})

    # ── NFA simulation ────────────────────────────────────────────────────────

    def run(self, input_string: str) -> Tuple[bool, List[dict]]:
        """
        Simulate the NFA on *input_string* (subset / powerset construction at runtime).

        Returns
        -------
        accepted : bool
        trace    : list of step dicts
        """
        current_states = self.epsilon_closure({self.start_state})
        trace = [{
            "step": 0,
            "symbol": "START",
            "states": sorted(current_states),
            "accepted": bool(current_states & self.accept_states),
        }]

        for i, symbol in enumerate(input_string, start=1):
            next_states: Set = set()
            for s in current_states:
                next_states |= self.transitions.get((s, symbol), set())
            current_states = self.epsilon_closure(next_states)
            trace.append({
                "step": i,
                "symbol": symbol,
                "states": sorted(current_states),
                "accepted": bool(current_states & self.accept_states),
            })

        accepted = bool(current_states & self.accept_states)
        return accepted, trace

    def get_transitions_table(self) -> List[dict]:
        rows = []
        for (state, symbol), next_states in sorted(self.transitions.items(), key=str):
            rows.append({
                "Current State": state,
                "Input Symbol": symbol,
                "Next States": ", ".join(str(s) for s in sorted(next_states)),
            })
        return rows

    # ── NFA → DFA (subset construction) ──────────────────────────────────────

    def to_dfa(self) -> Tuple["DFA", Dict]:
        """
        Convert this NFA to an equivalent DFA using the subset construction.

        Returns
        -------
        dfa          : DFA object
        state_map    : mapping from frozenset(NFA states) → DFA state label
        """
        start_closure = self.epsilon_closure({self.start_state})
        dfa_states: Dict[FrozenSet, str] = {}
        counter = [0]

        def label(fs: FrozenSet) -> str:
            if fs not in dfa_states:
                dfa_states[fs] = f"D{counter[0]}"
                counter[0] += 1
            return dfa_states[fs]

        label(start_closure)
        worklist = deque([start_closure])
        dfa_transitions: Dict[Tuple, str] = {}
        visited: Set[FrozenSet] = set()

        while worklist:
            current_set = worklist.popleft()
            if current_set in visited:
                continue
            visited.add(current_set)
            cur_label = label(current_set)

            for sym in self.alphabet:
                next_states: Set = set()
                for s in current_set:
                    next_states |= self.transitions.get((s, sym), set())
                next_closure = self.epsilon_closure(next_states)
                nxt_label = label(next_closure)
                dfa_transitions[(cur_label, sym)] = nxt_label
                if next_closure not in visited:
                    worklist.append(next_closure)

        dfa_accept = {
            label(fs)
            for fs in dfa_states
            if fs & self.accept_states
        }

        dfa = DFA(
            states=set(dfa_states.values()),
            alphabet=self.alphabet,
            transitions=dfa_transitions,
            start_state=label(start_closure),
            accept_states=dfa_accept,
        )
        # Build a human-readable state map
        state_map = {label(fs): sorted(fs) for fs in dfa_states}
        return dfa, state_map


# ─────────────────────────────────────────────────────────────────────────────
# Password-Validation DFA builder
# ─────────────────────────────────────────────────────────────────────────────

def build_password_dfa(min_length: int = 8) -> DFA:
    """
    DFA that accepts passwords satisfying ALL of the following rules:
      • At least *min_length* characters
      • Contains at least one uppercase letter
      • Contains at least one lowercase letter
      • Contains at least one digit
      • Contains at least one special character (!@#$%^&*_-)

    States encode progress as a bitmask:
      bit 0 → has_upper
      bit 1 → has_lower
      bit 2 → has_digit
      bit 3 → has_special

    Each state also needs a length counter; we combine bitmask with a length
    indicator: states are tuples (length_bucket, bitmask) where length_bucket
    saturates at min_length.
    """
    import string

    specials = set("!@#$%^&*_-")
    uppers   = set(string.ascii_uppercase)
    lowers   = set(string.ascii_lowercase)
    digits   = set(string.digits)
    all_chars = uppers | lowers | digits | specials

    # symbol categories for the alphabet
    def categorise(ch: str) -> Optional[str]:
        if ch in uppers:   return "upper"
        if ch in lowers:   return "lower"
        if ch in digits:   return "digit"
        if ch in specials: return "special"
        return "other"

    alphabet = {"upper", "lower", "digit", "special", "other"}
    max_len = min_length  # saturate at exactly min_length

    # States: (length: 0..max_len, bitmask: 0..15)
    states = {(l, m) for l in range(max_len + 1) for m in range(16)}
    states.add("DEAD")

    transitions = {}
    for length in range(max_len + 1):
        for mask in range(16):
            state = (length, mask)
            for sym_cat in alphabet:
                new_len = min(length + 1, max_len)
                if sym_cat == "upper":
                    new_mask = mask | 0b0001
                elif sym_cat == "lower":
                    new_mask = mask | 0b0010
                elif sym_cat == "digit":
                    new_mask = mask | 0b0100
                elif sym_cat == "special":
                    new_mask = mask | 0b1000
                else:
                    # other character — penalty: reject, go to DEAD
                    transitions[(state, sym_cat)] = "DEAD"
                    continue
                transitions[(state, sym_cat)] = (new_len, new_mask)

    # DEAD absorbs everything
    for sym_cat in alphabet:
        transitions[("DEAD", sym_cat)] = "DEAD"

    accept_states = {(max_len, 0b1111)}  # all 4 criteria met AND min length

    # Wrap with a character-level runner that maps chars → categories
    class PasswordDFA(DFA):
        def run(self, password: str) -> Tuple[bool, List[dict]]:  # type: ignore[override]
            current = self.start_state
            trace = [{"step": 0, "symbol": "START", "from": None, "to": str(current), "accepted": False}]
            for i, ch in enumerate(password, start=1):
                cat = categorise(ch)
                key = (current, cat)
                next_state = self.transitions.get(key, "DEAD")
                trace.append({
                    "step": i,
                    "symbol": ch,
                    "category": cat,
                    "from": str(current),
                    "to": str(next_state),
                    "accepted": next_state in self.accept_states,
                })
                current = next_state
            accepted = current in self.accept_states
            strength = _password_strength(password, accepted)
            return accepted, trace, strength

    return PasswordDFA(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        start_state=(0, 0),
        accept_states=accept_states,
    )


def _password_strength(password: str, accepted: bool) -> dict:
    """Return a breakdown of password strength criteria."""
    import string
    specials = set("!@#$%^&*_-")
    criteria = {
        "min_length_8": len(password) >= 8,
        "has_uppercase": any(c.isupper() for c in password),
        "has_lowercase": any(c.islower() for c in password),
        "has_digit":     any(c.isdigit() for c in password),
        "has_special":   any(c in specials for c in password),
    }
    score = sum(criteria.values())
    level = ["Very Weak", "Weak", "Fair", "Good", "Strong", "Very Strong"][score]
    return {"criteria": criteria, "score": score, "level": level, "accepted": accepted}


# ─────────────────────────────────────────────────────────────────────────────
# SQL-Injection Detection NFA builder
# ─────────────────────────────────────────────────────────────────────────────

def build_sql_injection_nfa() -> NFA:
    """
    NFA that detects common SQL-injection substrings (case-insensitive via
    character categories) in arbitrary input text.

    Patterns detected (as case-insensitive substrings):
      • ' OR '1'='1   (classic tautology)
      • UNION SELECT   (data extraction)
      • DROP TABLE     (destructive)
      • --             (comment bypass)
      • 1=1            (tautology)
      • ; (semicolon)  (statement termination)
      • xp_           (stored procedure prefix)
      • SLEEP(         (time-based blind)
      • EXEC(
    """
    # We model this as a multi-pattern NFA where:
    #   q0 (start) ε-transitions to each pattern's start state.
    #   Each pattern has its own chain of states.
    #   From any state we can also ε-skip (loop on any char at q0 for repeated matching).
    #
    # For simplicity we pre-lowercase input and match symbol by symbol.

    # Patterns (already lowercased)
    patterns = [
        "' or '1'='1",
        "union select",
        "drop table",
        "--",
        "1=1",
        ";",
        "xp_",
        "sleep(",
        "exec(",
        "' or 1=1",
        "insert into",
        "delete from",
    ]

    states: Set = {"q0"}
    transitions: Dict[Tuple, Set] = defaultdict(set)
    accept_states: Set = set()
    alphabet: Set[str] = set()

    state_counter = [1]

    for pat in patterns:
        prev = "q0"
        chain = []
        for ch in pat:
            s = f"q{state_counter[0]}"
            state_counter[0] += 1
            states.add(s)
            chain.append(s)
            transitions[(prev, ch)].add(s)
            alphabet.add(ch)
            prev = s
        # last state in chain is accepting
        accept_states.add(prev)

    # q0 self-loops on every character (so we can match anywhere in the string)
    # We collect the full alphabet used plus a wildcard approach:
    # Add a "wildcard" ε-back-loop from q0 to q0 on any symbol not starting a pattern.
    # Actually, we achieve "substring matching" by: from q0, for every symbol,
    # stay in q0 (self-loop), PLUS follow any matching transitions.
    full_alphabet = set()
    for (s, sym) in list(transitions.keys()):
        if sym != EPSILON:
            full_alphabet.add(sym)

    # q0 self-loop for all known symbols (makes it match anywhere)
    for sym in full_alphabet:
        transitions[("q0", sym)].add("q0")

    # Also add a generic "other" self-loop category for unlisted chars
    # (handled in the NFA runner by mapping unknown chars to None / skip)

    return NFA(
        states=states,
        alphabet=full_alphabet,
        transitions=dict(transitions),
        start_state="q0",
        accept_states=accept_states,
    )


def run_sql_nfa(nfa: NFA, text: str) -> Tuple[bool, List[str], List[dict]]:
    """
    Run the SQL-injection NFA on lowercased *text*.

    Returns
    -------
    detected        : bool
    matched_patterns: list of found patterns
    trace           : NFA trace
    """
    lowered = text.lower()

    # Run full NFA simulation
    current_states = nfa.epsilon_closure({nfa.start_state})
    trace = [{
        "step": 0,
        "symbol": "START",
        "states": sorted(current_states),
        "accepted": bool(current_states & nfa.accept_states),
    }]

    for i, ch in enumerate(lowered, start=1):
        next_states: Set = set()
        for s in current_states:
            next_states |= nfa.transitions.get((s, ch), set())
            # fallback: if ch not in alphabet, stay in q0
            if not nfa.transitions.get((s, ch)):
                if s == "q0":
                    next_states.add("q0")
        current_states = nfa.epsilon_closure(next_states)
        trace.append({
            "step": i,
            "symbol": ch,
            "states": sorted(current_states),
            "accepted": bool(current_states & nfa.accept_states),
        })

    detected = bool(current_states & nfa.accept_states)

    # Find which patterns are present (simple substring detection for reporting)
    patterns = [
        "' or '1'='1", "union select", "drop table", "--",
        "1=1", ";", "xp_", "sleep(", "exec(",
        "' or 1=1", "insert into", "delete from",
    ]
    matched = [p for p in patterns if p in lowered]

    return detected, matched, trace
