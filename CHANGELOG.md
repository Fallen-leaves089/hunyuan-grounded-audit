# Changelog

## 0.2.0 - 2026-11-20

- Align the model profile with Tencent's official Hy4 preview (`hy4-preview`) and restrict HY4-specific compensation to the documented long-thinking and excessive self-verification limitation.
- Explicitly isolate historical HY3 observations and model-neutral audit risks from HY4 conclusions; version changes require new evidence.
- Add WorkBuddy as a second supported host, including upload/package guidance, project-level `.codebuddy/skills/`, default-permission boundaries, workspace context, memory, connectors, and unverified items.
- Add `scripts/package_workbuddy.py` and contract/packaging tests for a deterministic upload archive rooted at `project-health-audit/`.
- Clarify the license boundary: the related `project-health` main project remains noncommercial, while this ecosystem skill is fully open source under Apache-2.0.
- Simplify the feedback request to the problem encountered, the model used, and the shell/host used.

## 0.1.1 - 2026-11-18

- Standardize host/model-specific repository metadata, README labels, and release packaging.
- Publish downloadable archives with SHA-256 checksums.
- Separate deterministic package and contract checks from model-behavior evidence in the README and model-eval record format.

## 0.1.0 - 2026-11-18

- Split `hunyuan-grounded-audit` out of the combined `grounded-audit` package.
- Specialize the audit skill for Tencent CodeBuddy Code CLI/TUI and Tencent Hunyuan.
- Keep the evidence-first audit method, read-only default, memory recorder, package verifier and Apache-2.0 licensing.
- Revalidate the host contract against the official `cnb.cool/codebuddy/codebuddy-code` snapshot at `c318ed39de3a3ed3d8b4b3864c631677f17948e4` (version `2.185.0`).
- Compensate for the CodeBuddy Plan Mode inheritance gap, wider subagent modes, non-blocking hook errors, project-skill shadowing, inline skill commands, parent memory discovery, project allow trust and non-interactive trust bypass.
- Add Hunyuan-specific risk hypotheses and HY1-HY10 behavior evaluations without treating public benchmark scores as project evidence.
