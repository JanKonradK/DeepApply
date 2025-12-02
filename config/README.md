# Configuration

This directory contains the policy and configuration files that control the behavior of the Nyx Venatrix agents.

## Files

### `effort_policy.yml`
**Purpose**: Defines the rules for determining effort levels.
- **Thresholds**: Match score percentages that trigger Low, Medium, or High effort.
- **Rules**: Logic for upgrading or downgrading effort (e.g., "Always High effort for Top Tier companies").
- **QA**: Conditions that trigger mandatory QA reviews.

### `stealth.yml`
**Purpose**: Configures anti-detection and stealth measures.
- **Domain Limits**: Max applications per day/hour for specific domains (LinkedIn, Indeed, etc.).
- **Delays**: Configuration for randomized delays (inter-action, inter-application).
- **Browser**: Fingerprinting settings.

### `profile.json`
**Purpose**: The "Truth Source" for the QA Agent.
- **skills_true**: A list of skills the user *actually* possesses.
- **skills_false**: A list of skills the user *does not* have. The QA agent uses this to detect hallucinations.
- **validation_rules**: Constraints for generated content (e.g., max years of experience to claim).

## Usage

These files are loaded by the Agent service at startup. Changes require a service restart to take effect.
