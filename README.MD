# Discord Issue Bot

This Discord bot allows users to create GitHub issues directly from Discord using slash commands and interactive modals. It's designed to streamline the process of reporting bugs and suggesting features by providing a user-friendly interface for non-technical users.

## Features

- **Slash Commands**: The bot uses Discord's slash commands to provide a clean and intuitive user experience.
- **Interactive Modals**: When a user initiates the issue reporting process, the bot presents a modal to collect the necessary information.
- **Automatic Issue Creation**: The bot automatically creates a GitHub issue with the information provided by the user.
- **Customizable Labels**: The bot can be configured to apply different labels to bug reports and suggestions.

## Setup

To get started, you'll need to create a `.env` file in the root of the repository with the following variables:

```
DISCORD_TOKEN=your_discord_bot_token
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO=your_username/your_repo_name
```

### 1. Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and create a new application.
2. In the "Bot" tab, click "Add Bot" and copy the token. This is your `DISCORD_TOKEN`.
3. Enable the "Message Content Intent" under "Privileged Gateway Intents".
4. In the "OAuth2" tab, click on "URL Generator" and select the `bot` and `applications.commands` scopes.
5. In the "Bot Permissions" section, select the following permissions:
   - `Send Messages`
   - `Read Message History`
   - `Use Slash Commands`
6. Copy the generated URL and paste it into your browser to invite the bot to your server.

### 2. Create a GitHub Personal Access Token

1. Go to your GitHub [Developer settings](https://github.com/settings/tokens) and click "Generate new token".
2. Give the token a descriptive name and select the `repo` scope.
3. Click "Generate token" and copy the token. This is your `GITHUB_TOKEN`.

### 3. Set the GitHub Repository

Set the `GITHUB_REPO` variable to the full name of the repository where you want to create issues (e.g., `your_username/your_repo_name`).

## Usage

To report a bug or suggest a feature, use the `/report issue` slash command. The bot will respond with a message containing two buttons: "Bug Report" and "Suggestion". Clicking one of these buttons will open a modal where you can enter the title and description of the issue.

Alternatively, the bot will automatically prompt you to create an issue if your message contains keywords like "bug", "issue", "error", "problem", "suggestion", "idea", "feature", or "improve".
