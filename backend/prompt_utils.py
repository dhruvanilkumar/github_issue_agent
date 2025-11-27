def build_prompt(issue_data):
    """
    Build a comprehensive prompt for Gemini to analyze GitHub issues.
    Includes system role, clear instructions, schema, and example.
    """
    title = issue_data.get('title', '')
    body = issue_data.get('body', '')
    comments = issue_data.get('comments', [])
    
    # Truncate body if too long to avoid token limits
    if len(body) > 4096:
        body = body[:4096] + "...[truncated]"
    
    # Format comments
    comments_text = ""
    if comments:
        comments_text = "\n\nComments from other users:\n"
        for i, comment in enumerate(comments[:10], 1):  # Limit to first 10 comments
            if len(comment) > 500:
                comment = comment[:500] + "...[truncated]"
            comments_text += f"  {i}. {comment}\n"
    else:
        comments_text = "\n\nNo comments on this issue yet."
    
    prompt = f"""You are an expert GitHub issue analyzer. Your task is to analyze GitHub issues and provide structured insights that help maintainers and contributors understand and prioritize issues effectively.

You will receive:
1. Issue title
2. Issue body/description (may be empty or very long)
3. Comments from other users (may be empty)

Your job is to analyze all this information and respond with ONLY a valid JSON object using exactly this schema (no markdown, no preamble, just pure JSON):

{{
  "summary": "A concise one-sentence summary of the main problem, feature request, or question.",
  "type": "bug | feature_request | documentation | question | other",
  "priority_score": "A number from 1 (low priority) to 5 (critical priority), followed by a brief justification (1-2 sentences).",
  "suggested_labels": ["label1", "label2", "label3"],
  "potential_impact": "A brief 1-2 sentence description of the potential impact on users if this is a bug, or value added if it's a feature."
}}

Guidelines:
- "summary" must be exactly ONE sentence
- "type" must be one of: bug, feature_request, documentation, question, other
- "priority_score" format: "X - [justification]" where X is 1-5
- "suggested_labels" should be 2-4 relevant GitHub labels (standard ones like "bug", "enhancement", "good first issue", "help wanted", etc.)
- "potential_impact" should be practical and user-focused

Example:
Input:
  Title: TypeError when calling updateProfile without authentication
  Body: When I call updateProfile() while not authenticated, the app throws a TypeError and crashes.
  Comments: User 1: "Same issue here on v2.1" | User 2: "This is blocking our release"

Output (pure JSON, nothing else):
{{
  "summary": "Calling updateProfile without authentication causes a TypeError crash.",
  "type": "bug",
  "priority_score": "4 - Users experience app crash; blocks release; needs urgent fix.",
  "suggested_labels": ["bug", "crash", "authentication"],
  "potential_impact": "Users without authentication cannot use the app and experience complete failure; data integrity at risk."
}}

---

Now analyze this GitHub issue:

Title: {title}

Body:
{body if body else "[No description provided]"}

{comments_text}

Return ONLY the JSON object, no other text."""

    return prompt
