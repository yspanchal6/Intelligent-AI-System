# Security Notes

## Secrets and configuration

- Keep `.env` out of version control.
- Use `.env.example` only for variable names and safe placeholders.
- If a real API key has ever been committed or shared, revoke/rotate it through the provider and remove it from the repository history as appropriate.
- Do not publish API keys, access tokens, personal phone numbers, or private task data in screenshots.

## Local data

- Task data is stored in local JSON and should be treated as plain text unless the implementation explicitly adds encryption.
- Back up task data before editing it manually.
- Do not commit personal `tasks.json` or generated notes.

## External actions

- Review confirmation prompts carefully.
- A WhatsApp draft is not the same as sending a message; review the recipient and text before sending manually.
- Do not add arbitrary shell execution or unrestricted file writing without a security review.

## GitHub publication checklist

- [ ] Remove `.env` and verify no credentials are present in tracked files.
- [ ] Exclude `.venv/`, `venv/`, `__pycache__/`, `*.pyc`, and local generated data.
- [ ] Review screenshots for secrets and personal information.
- [ ] Run tests and record actual results.
- [ ] Verify every documented command and feature against the source.
- [ ] Add a license only if you intend to define reuse permissions.
- [ ] Review dependency versions and update them deliberately rather than blindly.
