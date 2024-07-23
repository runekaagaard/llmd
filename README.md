# Large Language Model Markdown Format (LLMD) Specification

## 1. Introduction

The Large Language Model Markdown Format (LLMD) is a structured text format designed to facilitate natural language
interactions between human users and Large Language Models (LLMs) in programming contexts. This document specifies the
structure, components, and usage of LLMD.

## 2. Document Structure

An LLMD document consists of the following sections in order:

1. Project Header
2. Meta Section (including Instructions and Tools)
3. Mission Section
4. Code Context Section
5. Changelog Section
6. Conversation Thread Section

### 2.1 Project Header

The project header is the first line of the document and follows this format:

```
# Project: [Project Name]
```

### 2.2 Meta Section

The meta section includes the format identifier, instructions, and available tools:

```markdown
## Meta: LLMD (Large Language Model Markdown Format)

[Description of LLMD and its purpose]

### Instructions
[List of instructions for using LLMD]

### Tools
[Description of available tools and their usage]
```

### 2.3 Mission Section

The mission section describes the main goal or purpose of the project:

```markdown
## Mission

[Project mission statement]
```

### 2.4 Code Context Section

The code context section contains the current state of the project's code files:

```markdown
## Code Context

### [filename.ext]
```[language]
[File content]
```
```

### 2.5 Changelog Section

The changelog section lists changes made to the project:

```markdown
## Changelog

- [Change description]
```

### 2.6 Conversation Thread Section

The conversation thread section contains the dialogue between the human and the LLM:

```markdown
## Conversation Thread

### Entry [Number]

**Human:** [Human's message]

**Assistant:** [LLM's response]
```

## 3. LLMD Tools

### 3.1 Code Modification (SEARCH / REPLACE)

The SEARCH / REPLACE tool is used for modifying existing code. The filepath must be specified before the SEARCH block:

```
[filepath]
<<<<<< SEARCH
[Original code]
=======
[Modified code]
>>>>>> REPLACE
```

### 3.2 Mission Update (SEARCH_MISSION / REPLACE_MISSION)

The SEARCH_MISSION / REPLACE_MISSION tool is used to update the project's mission statement:

```
<<<<<< SEARCH_MISSION
[Original mission statement]
=======
[Updated mission statement]
>>>>>> REPLACE_MISSION
```

### 3.3 Changelog Addition (CHANGELOG)

The CHANGELOG tool is used to add entries to the project's changelog:

```
<<<<<< CHANGELOG
[Change description]
>>>>>> CHANGELOG
```

## 4. Usage Guidelines

### 4.1 Code Modification

When modifying code:

- Specify the filepath before the SEARCH block
- Include enough context in the SEARCH block to uniquely identify the code section
- Provide the complete updated code in the REPLACE block

### 4.2 Mission Update

When updating the mission:

- Include the entire current mission statement in the SEARCH_MISSION block
- Provide the complete new mission statement in the REPLACE_MISSION block

### 4.3 Changelog Addition

When adding to the changelog:

- Provide a concise description of the change
- Each entry will be automatically formatted as a list item

## 5. Best Practices

- Maintain clear and concise communication in the conversation thread
- Use code blocks for code snippets or examples within the conversation
- Keep the code context up-to-date with all changes made during the conversation
- Add changelog entries for all significant changes or additions to the project
- Refer to specific line numbers or functions when discussing code to maintain clarity

## 6. Security Considerations

When implementing LLMD:

- Validate and sanitize all inputs to prevent potential security issues
- Implement appropriate access controls for code modification operations
- If code execution is implemented, ensure it's done in a secure, sandboxed environment
