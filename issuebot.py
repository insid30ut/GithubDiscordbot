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
    """Creates a new issue on the configured GitHub repository.

    Args:
        title (str): The title of the GitHub issue.
        body (str): The body content of the GitHub issue.
        label (str): The label to apply to the GitHub issue.

    Returns:
        str: The URL of the newly created GitHub issue, or None if creation fails.
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
    """Prints a message to the console when the bot is successfully connected."""
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message):
    """Event handler for when a message is sent to a channel.

    This function listens for messages containing keywords related to bugs or
    suggestions and prompts the user to create a GitHub issue.

    Args:
        message (discord.Message): The message object from the Discord API.
    """
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    content = message.content.lower()
    # Keywords to trigger the bot
    bug_keywords = ["bug", "issue", "error", "problem"]
    suggestion_keywords = ["suggestion", "idea", "feature", "improve"]

    # Check if the message contains any of the keywords
    if any(keyword in content for keyword in bug_keywords) or any(keyword in content for keyword in suggestion_keywords):
        # Respond with the view to the user's message
        view = MainView(message_content=message.content)
        await message.reply(
            embed=discord.Embed(
                title="Did you want to report an issue or suggest a feature?",
                description="Click a button below to get started."
            ),
            view=view
        )
        return # Stop processing to avoid conflicts if other commands are added


report = bot.create_group("report", "Report a bug or suggest a feature")

@report.command(name="issue", description="Report a bug or suggest a feature")
async def issue(ctx):
    """Slash command to initiate the issue reporting process.

    This command displays a view with buttons to report a bug or suggest a feature.

    Args:
        ctx (discord.ApplicationContext): The context of the slash command.
    """
    await ctx.respond(embed=discord.Embed(title="Report an issue or suggest a feature"), view=MainView())


class MainView(discord.ui.View):
    """A Discord UI View that presents buttons for creating bug reports or suggestions.

    This class creates a view with two buttons: "Bug Report" and "Suggestion".
    When a button is clicked, it opens a modal for the user to enter the
    details of their report.

    Attributes:
        message_content (str, optional): The content of the message that
            triggered the view. Defaults to None.
    """
    def __init__(self, message_content: str = None) -> None:
        super().__init__(timeout=None)
        self.message_content = message_content

    @discord.ui.button(
        label="Bug Report", style=discord.ButtonStyle.red, custom_id="bug"
    )
    async def button_callback(self, button, interaction):
        """Callback for the "Bug Report" button.

        This function is executed when a user clicks the "Bug Report" button.
        It opens a modal for the user to enter the bug report details.

        Args:
            button (discord.ui.Button): The button that was clicked.
            interaction (discord.Interaction): The interaction object from the
                Discord API.
        """
        await interaction.response.send_modal(ReportModal(issue_type="bug", message_content=self.message_content))

    @discord.ui.button(
        label="Suggestion", style=discord.ButtonStyle.green, custom_id="suggestion"
    )
    async def button_callback2(self, button, interaction):
        """Callback for the "Suggestion" button.

        This function is executed when a user clicks the "Suggestion" button.
        It opens a modal for the user to enter the suggestion details.

        Args:
            button (discord.ui.Button): The button that was clicked.
            interaction (discord.Interaction): The interaction object from the
                Discord API.
        """
        await interaction.response.send_modal(
            ReportModal(issue_type="suggestion", message_content=self.message_content)
        )


class ReportModal(discord.ui.Modal):
    """A Discord UI Modal for submitting bug reports or suggestions.

    This class creates a modal with input fields for a title and description.
    When the user submits the modal, it creates a GitHub issue with the
    provided information.

    Attributes:
        issue_type (str): The type of issue, either "bug" or "suggestion".
        message_content (str, optional): The content of the message that
            triggered the modal. Defaults to None.
    """
    def __init__(self, issue_type: str, message_content: str = None) -> None:
        self.issue_type = issue_type
        super().__init__(title=f"{issue_type.capitalize()} Report")
        self.add_item(
            discord.ui.InputText(
                label="Title",
                placeholder=f"Title of your {issue_type} report",
                style=discord.InputTextStyle.short,
                max_length=50,
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Description",
                placeholder=f"Description of your {issue_type} report",
                style=discord.InputTextStyle.long,
                max_length=1000,
                value=message_content,
            )
        )

    async def callback(self, interaction: discord.Interaction):
        """Callback for the modal submission.

        This function is executed when a user submits the modal. It creates a
        GitHub issue with the provided information and sends a confirmation
        message to the user.

        Args:
            interaction (discord.Interaction): The interaction object from the
                Discord API.
        """
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
            embed.add_field(name="Description", value=f"```{description}```", inline=False)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"❌ Sorry, {interaction.user.mention}. There was an error creating the GitHub issue.")

# --- Run the Bot ---
if __name__ == "__main__":
    print("Starting bot...")
    bot.run(DISCORD_TOKEN)