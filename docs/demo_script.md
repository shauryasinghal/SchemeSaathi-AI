# Demo Script — 10 Minute OOSC 4.0 Presentation

Written to be spoken naturally, not read verbatim. Adjust the exact
wording to how you actually talk, but keep the structure and timing --
judges are watching the clock too.

---

## 0:00 – 1:00 | Problem

"India has over 4,700 central and state government schemes on myScheme
alone -- covering farmers, students, artisans, street vendors, people with
disabilities. The problem isn't that these schemes don't exist. It's that
most people eligible for them never find out. Eligibility criteria are
written in dense, formal language, spread across dozens of separate
government websites, and mostly available only in English."

"Underserved communities -- exactly the people these schemes are meant
for -- are the ones least equipped to search through all of that."

## 1:00 – 2:00 | Why existing scheme discovery is difficult

"myScheme itself is a great platform, but it's built for someone who
already knows roughly what to search for, and is comfortable reading
government English. If you're a farmer in rural Bihar without a lot of
formal schooling, that's a real barrier -- not because the information
doesn't exist, but because of how it's presented."

## 2:00 – 3:00 | SchemeSaathi solution

"SchemeSaathi lets you describe your own situation, in your own words --
in English, Hindi, or a mix -- and it tells you which schemes you may
actually qualify for, why, what's missing to be sure, what documents
you'd need, and how to apply. Every recommendation links back to the
official government source, so nothing is a black box."

## 3:00 – 5:00 | Live farmer demo

[Click the "Farmer" quick example, or type a live query.]

"Let's try it live. I'm a farmer from Uttar Pradesh, I have 2 acres of
land, and I need help with irrigation."

[Click "Find My Schemes." Walk through the result as it appears:]

"Notice it's not just returning a keyword match -- it retrieved PM-KISAN
for income support and PM Krishi Sinchayee Yojana specifically for
irrigation, explained why each one fits, and told me exactly what
documents I'd need."

## 5:00 – 6:30 | Eligibility reasoning

"This is the part we think matters most for trust. Each scheme here shows
a match level -- High, Medium, or Needs More Information -- never '100%
eligible,' because we're not the government and we can't promise that.
You can see exactly what matched my profile, what's still missing, and
if something doesn't fit, it tells you that honestly instead of forcing a
recommendation."

## 6:30 – 7:30 | Hindi demonstration

[Switch the language selector to Hindi, re-run a query or point to a
cached result.]

"The exact same reasoning, in simple Hindi -- not stiff, bureaucratic
Hindi, but how you'd actually explain this to a neighbour. This matters
because a big part of who these schemes are for may be more comfortable
reading in their own language than in English."

## 7:30 – 8:30 | RAG / source transparency

"Under the hood, this is a retrieval-augmented generation pipeline. We
embed the person's situation, search a local vector index of our scheme
database, and only then does the language model explain what was
retrieved -- it's explicitly instructed to never invent a scheme or a
benefit. And every single recommendation links to the actual government
source page, so you never have to just take the AI's word for it."

## 8:30 – 9:15 | Social impact

"Our goal isn't to replace myScheme -- it's to be the plain-language front
door to it. Better discoverability, less information asymmetry, and
genuine multilingual access for the communities these schemes were
written for in the first place."

## 9:15 – 10:00 | Scalability / future roadmap

"Right now we're running on 45 well-known central schemes as our Phase 1
dataset. The architecture is built to scale straight to hundreds of
central and state schemes with no redesign. Beyond that: Bhashini
integration for more Indian languages plus voice input, so someone who
can't type can just speak their situation; a WhatsApp front-end for
last-mile reach; and state-specific scheme expansion. Thank you."

---

**Timing note:** rehearse this once with a stopwatch before Phase 1
submission. Live demos run long -- if you're tight on time, cut the
Hindi segment to 30 seconds rather than rushing the eligibility-reasoning
explanation, since that's the section judges are most likely to probe on.
