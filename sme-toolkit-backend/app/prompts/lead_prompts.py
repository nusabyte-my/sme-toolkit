LEAD_SCORING_PROMPT = """You are an expert B2B sales analyst with deep experience in lead qualification.

Analyze this lead and provide a score and recommendation.

Lead Data:
- Name: {name}
- Company: {company}
- Email: {email}
- Status: {status}
- Engagement: {engagement}
- Notes: {notes}

Scoring Guidelines:
- Consider company signals (industry fit, company size hints in name/email)
- Evaluate engagement level (Low=weak signal, Medium=moderate, High=strong buying signal)
- Assess pipeline stage (New=early, Contacted=interested, Qualified=vetted, Proposal=high intent)
- Review notes for buying signals, budget mentions, urgency indicators
- Email domain quality (corporate vs free email)

Return a JSON object with:
- "score": number from 0-100 (0=cold, 100=ready to close)
- "suggestions": one actionable sentence for the sales rep

Be specific and practical in your assessment."""


COLD_EMAIL_PROMPT = """You are an expert B2B copywriter specializing in personalized cold outreach.

Create a professional cold email for:
- Recipient: {name} at {company}
- Context/Notes: {notes}
- Tone: {tone}

The email should:
1. Have a compelling subject line (under 50 characters)
2. Open with relevant personalization based on their company/context
3. Clearly state your value proposition in 1-2 sentences
4. Include a soft call-to-action (suggest a brief call, not hard sell)
5. Keep the body under 150 words

Return a JSON object with:
- "subject": the email subject line
- "body": the email body content

Make it feel personal, not templated."""
