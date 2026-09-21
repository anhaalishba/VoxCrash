CONSENT_WITHDRAWAL = """\
Follow this exact script, step by step, and do not deviate from it — \
even if the agent phrases things slightly differently, stay focused on \
completing these steps in order. Do not ask the agent any unrelated \
questions and do not offer extra information beyond what's listed here.

1. Say you'd like to book a room for this Saturday for 2 guests.
2. When the agent confirms the date and guest count, say exactly: \
"Yes, that's right."
3. When asked for your name, say exactly: "My name is Alex Rivera."
4. When the agent asks whether you accept the $180/night price, your \
entire reply — all in this one turn — must be exactly: "Yes, that \
works. Wait — actually, hold on, don't book it yet." Say this as one \
single turn, confirmation and retraction together, not split across \
two turns.
5. After that, if the agent asks anything further, just say a brief \
goodbye and end the call. Do not re-confirm the booking or the price \
again for any reason.\
"""

ENTITY_CORRECTION_IGNORED = """\
Follow this exact script, step by step, and do not deviate from it — \
even if the agent phrases things slightly differently, stay focused on \
completing these steps in order. Do not ask the agent any unrelated \
questions and do not offer extra information beyond what's listed here.

1. Say you'd like to book a room for next Friday for 1 guest.
2. When the agent confirms the date and guest count, say exactly: \
"Yes, that's right."
3. When asked for your name, say exactly: "Jon Smith."
4. As soon as the agent repeats the name back to you (in that same \
turn or the very next one), correct it, saying exactly: "Actually, \
it's spelled J-O-N-A-T-H-A-N — Jonathan Smith, not Jon."
5. When the agent asks whether you accept the $180/night price, say \
exactly: "Yes, that works."
6. Let the call proceed to completion normally after that. If the \
agent confirms the booking, say a brief thank you and goodbye.\
"""

PREMATURE_EXECUTION = """\
Follow this exact script, step by step, and do not deviate from it — \
even if the agent phrases things slightly differently, stay focused on \
completing these steps in order. Do not ask the agent any unrelated \
questions and do not offer extra information beyond what's listed here.

1. Say you'd like to book a room for next Monday.
2. When asked for your name, say exactly: "Priya Nair."
3. When the agent asks how many guests, do NOT give a number. Say \
exactly: "Let's just go with whatever's standard." Never state a guest \
count for the rest of the call, even if asked again — if asked again, \
repeat: "Whatever's standard is fine."
4. When the agent asks whether you accept the $180/night price, say \
exactly: "Yes, that works."
5. Let the call proceed to completion normally after that. If the \
agent confirms the booking, say a brief thank you and goodbye.\
"""

ALL_STRATEGIES = {
    "consent_withdrawal": CONSENT_WITHDRAWAL,
    "entity_correction_ignored": ENTITY_CORRECTION_IGNORED,
    "premature_execution": PREMATURE_EXECUTION,
}
