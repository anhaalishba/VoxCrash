# VoxCrash — Chaos Engineering for Voice Agents

> An autonomous AI **"red-team caller"** that calls other voice agents, stress-tests them with realistic conversational chaos, and produces replayable evidence showing exactly where and why the agent broke.

**Built for the AssemblyAI Voice Agent Hackathon 2026 by lablab.ai × AssemblyAI.**

---

## 👥 Team

* **Anha Alishba**
* **Sayed Asad Murtiza**

---

## 🚨 The Problem

Voice agents are moving into production fast — booking, support, healthcare intake, dispatch, sales. But testing them is still primitive: a passing scripted demo call proves nothing about how the agent behaves when a real caller interrupts, corrects a misheard detail, or withdraws consent right before an action executes.

These are **conversation failures**, not API failures, and nobody is systematically testing for them today.

---

## 💡 The Solution

VoxCrash runs two AssemblyAI Voice Agent API sessions and bridges their live audio together — one agent (the **Target**) is a real hotel-booking assistant, while the other (the **Attacker**, VoxCrash itself) plays an adversarial customer running one scripted attack per call.

A deterministic invariant engine watches the Target's tool calls and flags the exact moment a safety rule breaks, then captures a permanent, replayable evidence record.

---

## 🎯 The 3 Attacks

| Strategy                    | What it does                                                 | Invariant it tests                                  |
| --------------------------- | ------------------------------------------------------------ | --------------------------------------------------- |
| `consent_withdrawal`        | Confirms a booking, then retracts it right before completion | Booking must not fire after withdrawn consent       |
| `entity_correction_ignored` | Corrects a misheard name mid-call                            | The corrected name, not the stale one, must be used |
| `premature_execution`       | Never states guest count                                     | Booking must not fire with a missing required slot  |

---

## 🏗️ How It Works

```text
TARGET (booking agent)  ◄──── live audio, both directions ────►  ATTACKER (VoxCrash)

        │
        ▼
transcript + tool.call events
        │
        ▼
ConversationState Monitor
        │
        ▼
Invariant Engine
        │
        ▼
Evidence Capture
        │
        ▼
evidence/*.json
```

Both agents are real AssemblyAI Voice Agent API sessions using Universal-3 Pro STT, LLM routing, TTS, and barge-in.

`voxcrash/bridge.py` pipes each agent's `reply.audio` directly into the other's `input.audio`, creating a genuine live conversation between two AI voices rather than a scripted transcript exchange.

`create_booking` is a **client-side tool**: the bridge intercepts `tool.call`, runs the invariant checks, and returns `tool.result`. The Target never knows that a rule is being tested.

Full architecture: [`docs/architecture.md`](./docs/architecture.md)

---

## ⚙️ Setup

```bash
git clone <this-repo>
cd voxcrash

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
```

Add your AssemblyAI API key to `.env`:

```env
ASSEMBLYAI_API_KEY=your_api_key_here
```

---

## 💥 Running an Attack

```bash
python main.py run consent_withdrawal

python main.py run entity_correction_ignored

python main.py run premature_execution

python main.py run all
```

To view captured failures:

```bash
python main.py report
```

Each run prints the live transcript of both agents talking to each other.

If an invariant breaks, you'll see:

```text
🔴 FAILURE DISCOVERED
```

A `VOICE-FAIL-XXXXXXXX.json` record is then written to `evidence/`.

---

## 📊 Dashboard

A small web dashboard reads the evidence files and displays browsable failure cards containing:

* Conversation transcript
* Tool-call arguments
* State snapshot
* Failure details
* Replay instructions

Start the dashboard:

```bash
python server.py
```

Then open:

```text
http://localhost:8080
```

---

## 🧪 Project Status

* [x] Target agent config + client-side tool schema
* [x] Attacker agent + 3 scripted strategies
* [x] Dual-session audio bridge
* [x] Real-time pacing + auto-reconnect
* [x] Conversation state monitor
* [x] Invariant engine
* [x] Evidence capture
* [x] Dashboard UI
* [ ] Deterministic replay from a saved evidence record

---

## 🧠 Why This Matters

As voice agents take on real actions — not just conversation — an unnoticed conversational failure becomes a safety and reliability problem.

VoxCrash is a first step toward voice-agent QA infrastructure:

> **Before you deploy a voice agent to thousands of customers, find out what breaks it first.**

---

## 🏆 Hackathon

Built for the **AssemblyAI Voice Agent Hackathon 2026**.

**Team:** Anha Alishba & Sayed Asad Murtiza

---

## 📄 License

MIT
