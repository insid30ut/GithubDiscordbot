import discord
import os
import requests
import json
from discord.commands import SlashCommandGroup
from dotenv import load_dotenv

# Load environment variables. Create a .env file in the same directory:
# DISCORD_TOKEN=your_discord_bot_token
# GITHUB_TOKEN=your_github_personal_access_token
# GITHUB_REPO=your_username/your_repo_name
#
# or set them in your deployment environment.
load_dotenv()

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO = os.environ.get('GITHUB_REPO') # e.g., "octocat/Spoon-Knife"

if not all([DISCORD_TOKEN, GITHUB_TOKEN, GITHUB_REPO]):
    print("Error: Missing one or more environment variables.")
    print("Please set DISCORD_TOKEN, GITHUB_TOKEN, and GITHUB_REPO.")
    exit(1)

# --- GitHub API Function ---
def create_github_issue(title, body, label):
    """
    Creates a new issue on the configured GitHub repository.
    """
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    payload = {
        "title": title,
        "body": body,
        "labels": [label]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raise an exception for bad status codes
        
        # Return the URL of the newly created issue
        return response.json().get("html_url")
        
    except requests.exceptions.RequestException as e:
        print(f"Error creating GitHub issue: {e}")
        if response.content:
            print(f"Response content: {response.content}")
        return None

# --- Discord Bot Setup ---
# Define the intents your bot needs.
intents = discord.Intents.default()
intents.message_content = True # Required to read message content
intents.messages = True

# Use commands.Bot for easier command handling
bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    """Event handler for when the bot has connected to Discord."""
    print(f"Logged in as {bot.user}")


class ReportView(discord.ui.View):
    def __init__(self):
        # Timeout in seconds
        super().__init__(timeout=180)

    @discord.ui.select(
        placeholder="Choose the report type...",
        options=[
            discord.SelectOption(
                label="Bug Report",
                value="bug",
                description="Report a bug or issue."
            ),
            discord.SelectOption(
                label="Feature Suggestion",
                value="suggestion",
                description="Suggest a new feature or enhancement."
            ),
        ],
    )
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        """The callback function for the select menu."""
        issue_type = select.values[0]
        await interaction.response.send_modal(ReportModal(issue_type=issue_type))


@bot.slash_command(name="report", description="Submit a bug report or feature suggestion")
async def report(ctx: discord.ApplicationContext):
    """Shows a view with a select menu for picking bug or suggestion."""
    await ctx.response.send_message(
        "Please select the type of Github issue you'd like to submit:",
        view=ReportView(),
        ephemeral=True
    )


class ReportModal(discord.ui.Modal):
    def __init__(self, issue_type: str) -> None:
        self.issue_type = issue_type
        super().__init__(title=f"{issue_type.capitalize()} Report")
        self.add_item(
            discord.ui.InputText(
                label="Title",
                placeholder=f"Title of the {issue_type}",
                style=discord.InputTextStyle.short,
                max_length=50,
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Description",
                placeholder=f"Description of the {issue_type}",
                style=discord.InputTextStyle.long,
                max_length=1000,
            )
        )

    async def callback(self, interaction: discord.Interaction):
        title = self.children[0].value
        description = self.children[1].value

        # Create a descriptive title and body for the GitHub issue
        github_title = f"{self.issue_type.capitalize()}: {title}"
        github_body = (
            f"**{self.issue_type.capitalize()} Report from Discord**\n\n"
            f"**Reported by:** {interaction.user.name} (ID: {interaction.user.id})\n\n"
            f"**Title:** {title}\n"
            f"**Description:**\n{description}"
        )

        await interaction.response.send_message("Submitting to GitHub...", ephemeral=True)

        issue_url = create_github_issue(github_title, github_body, self.issue_type)

        if issue_url:
            embed = discord.Embed(
                title=f"{self.issue_type.capitalize()} Report Created",
                description=f"✅ Thanks, {interaction.user.mention}! Your {self.issue_type} report has been successfully created.",
                color=discord.Color.green() if self.issue_type == "suggestion" else discord.Color.red()
            )
            embed.add_field(name="Issue URL", value=f"[View on GitHub]({issue_url})", inline=False)
            embed.add_field(name="Title", value=title, inline=False)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"❌ Sorry, {interaction.user.mention}. There was an error creating the GitHub issue.")

# --- Run the Bot ---
if __name__ == "__main__":
    print("Starting bot...")
    bot.run(DISCORD_TOKEN)