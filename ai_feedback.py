"""
ai_feedback.py — Generates a personalized remark for a student's result.
----------------------------------------------------------------------------
Two modes:
1. AI mode — if OPENAI_API_KEY is set as an environment variable, sends the
   marks to OpenAI's Chat Completions API and returns a natural remark.
2. Rule-based mode — always available, no key needed, used automatically
   if no key is set or the API call fails.

SECURITY NOTE: this file never contains an API key. Set it in your terminal
before running the app, it is never written to disk here:
    Mac/Linux:   export OPENAI_API_KEY=your_key_here
    Windows:     set OPENAI_API_KEY=your_key_here
"""

import os
import json
import urllib.request


def generate_remark_rule_based(name, percentage):
    if percentage >= 90:
        return f"{name} has performed excellently and shows strong command over the subject."
    elif percentage >= 75:
        return f"{name} has performed well with a solid, consistent understanding."
    elif percentage >= 40:
        return f"{name} has passed but should put in more consistent effort to improve further."
    return f"{name} needs significant improvement and should revise the basics carefully."


def generate_remark_ai(name, course, marks_obtained, full_marks, percentage):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    prompt = (
        f"You are a teacher writing a short (max 2 sentence) report-card remark "
        f"for a student named {name}, enrolled in {course or 'their course'}. "
        f"They scored {marks_obtained} out of {full_marks} ({percentage}%). "
        f"Be specific, encouraging, and constructive. "
        f"Respond with ONLY the remark text, nothing else."
    )

    body = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 120,
    }).encode()

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"(AI remark failed, falling back to rule-based: {e})")
        return None


def generate_remark(name, course, marks_obtained, full_marks, percentage):
    ai_remark = generate_remark_ai(name, course, marks_obtained, full_marks, percentage)
    if ai_remark:
        return ai_remark
    return generate_remark_rule_based(name, percentage)
