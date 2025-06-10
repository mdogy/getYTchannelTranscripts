You are an expert analyst processing a YouTube video transcript. The transcript has been split into numbered sections (e.g., [1], [36], [56]). Your task is to read the provided transcript text and extract specific information, structuring your output in Markdown as requested. Do not use any external knowledge beyond the text provided. Cite all extracted information using the provided section numbers [i] where 'i' is the section number(s) supporting the statement. If a statement is supported by multiple sections, list all relevant section numbers [i, j, k].

**Video Metadata (from CSV):**
```json
{csv_row_data}
```

**Transcript Text:**
```
{transcript_text}
```

---

**Instructions:**

1.  **Identify Metadata:** From the provided CSV data and transcript, determine the video title, source URL, upload date, host name(s), and guest name(s). If any piece of metadata is not clearly present, indicate this in the output.
2.  **Summarize:** Create a detailed summary of 2-3 paragraphs covering the main discussion, key points, and flow of the conversation. Ensure all claims are supported by citations from the transcript.
3.  **Identify Main Topics:** List the primary subject areas discussed [Citations].
4.  **Extract Startup Ideas:** List and briefly describe any specific startup ideas presented or discussed in detail [Citations]. Include any associated metrics, potential business models, or target audiences mentioned for each idea [Citations].
5.  **Identify Common Insights/Themes:** Identify recurring or significant ideas, strategies, or philosophies discussed *within this specific transcript* [Citations]. These are themes that appear multiple times or are emphasized.
6.  **Extract Unique Insights/Key Takeaways:** Identify novel, counterintuitive, or particularly memorable points made specifically *in this transcript* [Citations]. These might be single impactful statements or strategies.
7.  **List Other People Mentioned:** Note any names of individuals mentioned in the conversation, excluding the primary host and guest(s) already identified [Citations].
8.  **List Tools/Technologies:** List any specific software, platforms, APIs, or technologies mentioned by name [Citations].
9.  **Describe Tool Usage:** For each tool/technology listed, describe *how* it is used or *what purpose* it serves according to the transcript [Citations].
10. **Extract Examples/Case Studies:** List any concrete examples or case studies used to illustrate points (e.g., specific companies, products, or personal anecdotes used as illustrations) [Citations].

---

Your output should follow this Markdown structure, filling in the details based *only* on the provided transcript text and including citations:

## Transcript Analysis

**Source Title:** [Insert Title Here - extracted from text if possible, otherwise note not found]
**Source URL:** [Insert URL Here - extracted from text if possible, otherwise note not found]
**Upload Date:** [Insert Date Here - extracted from text if possible, otherwise note not found]
**Host:** [Insert Host Name - extracted from text if possible, otherwise note not found]
**Guest(s):** [Insert Guest Name(s) - extracted from text if possible, otherwise note not found]

### Summary
[A detailed summary of 2-3 paragraphs covering the main discussion and key points from the transcript, with citations.]

### Main Topic(s)
[List the primary topics covered in the video, e.g., AI startup ideas, marketing strategies, specific tools, with citations.]

### Specific Startup Ideas Mentioned
*   **Idea Name/Description 1:** [Brief description] [Citations]
*   **Idea Name/Description 2:** [Brief description] [Citations]
    ... (List all distinct startup ideas mentioned)

### Common Insights/Themes (within this transcript)
[List overarching themes or insights discussed in this specific transcript that are likely to be relevant across the collection, with citations.]
*   [Insight 1] [Citations]
*   [Insight 2] [Citations]
    ...

### Unique Insights/Key Takeaways (within this transcript)
[List novel or particularly impactful points made specifically in this transcript, with citations.]
*   [Unique Insight 1] [Citations]
*   [Unique Insight 2] [Citations]
    ...

### Other People Mentioned (excluding main guest/host)
*   [Name 1] [Citations]
*   [Name 2] [Citations]
    ... (List any other individuals mentioned)

### Tools/Technologies Mentioned
*   [Tool Name 1] [Citations]
*   [Tool Name 2] [Citations]
    ... (List all specific tools or technologies mentioned)

### Tool Usage/Purpose
*   **[Tool Name 1]:** Used for [Specific use case mentioned in transcript] [Citations]
*   **[Tool Name 2]:** Used for [Specific use case mentioned in transcript] [Citations]
    ... (Describe the mentioned use for each tool)

### Specific Examples/Case Studies Mentioned
*   [Example/Case Study Name/Description 1] [Citations]
*   [Example/Case Study Name/Description 2] [Citations]
    ... (List any concrete examples or case studies used)
