# PR descriptions hard-wrapped for the terminal

## Observed incident

The agent drafted a PR description for `s22chan/project-suffix-remaining-launchers`
in a fenced block, wrapping every paragraph and list item at about 72 columns
like a commit message. The user pasted it into the GitHub web UI, where the
single line breaks stay as line breaks, and said:

> for PRs, the new lines kind of mess up wordwraps when pasting

## Behavior

A PR title and body are pasted into the web UI, so each paragraph and list item
goes on one line. A commit message, which stays in git and is read in a terminal,
keeps the 72-column wrap. Included: any text the agent drafts for the user to
paste into the GitHub UI (PR title and body). Excluded: commit messages, files
in the repository, and prose written in the terminal.

## Test arms

None run, so the effect is unverified. A replay would give fresh sessions the
branch summary and ask for the PR body, with and without the bullet, and count
bodies with a line break inside a paragraph.

## Outcome

Added one bullet to the "Git and review prose" section of `instructions/common.md`.
