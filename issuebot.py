import discord
import os
import requests
import json
from discord.ext import commands

# --- Configuration ---
# Load environment variables. Create a .env file in the same directory:
# DISCORD_TOKEN=your_discord_bot_token
# GITHUB_TOKEN=your_github_personal_access_token
# GITHUB_REPO=your_username/your_repo_name
#
# or set them in your deployment environment.

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
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Event handler for when the bot has connected to Discord."""
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('Bot is ready to receive commands.')
    print('------')

@bot.command(name='bug', help='Report a bug. Usage: !bug [detailed description]')
async def report_bug(ctx, *, description: str):
    """
    Command to report a bug.
    It takes all text after '!bug ' as the description.
    """
    if not description:
        await ctx.send("Please provide a description for the bug report. Usage: `!bug [description]`")
        return

    # Create a descriptive title and body for the GitHub issue
    title = f"Bug: {description[:50]}..." # Truncate title
    body = (
        f"**Bug Report from Discord**\n\n"
        f"**Reported by:** {ctx.author.name} (ID: {ctx.author.id})\n\n"
        f"**Description:**\n{description}"
    )
    
    await ctx.send(f"Submitting bug report to GitHub...")
    
    issue_url = create_github_issue(title, body, "bug")
    
    if issue_url:
        embed = discord.Embed(
            title="Bug Report Created",
            description=f"✅ Thanks, {ctx.author.mention}! Your bug report has been successfully created.",
            color=discord.Color.red()
        )
        embed.add_field(name="Issue URL", value=f"[View on GitHub]({issue_url})", inline=False)
        embed.add_field(name="Reported Bug", value=f"```{description}```", inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ Sorry, {ctx.author.mention}. There was an error creating the GitHub issue. Please notify an admin.")

@bot.command(name='suggest', help='Make a suggestion. Usage: !suggest [detailed description]')
async def make_suggestion(ctx, *, description: str):
    """
    Command to make a suggestion.
    It takes all text after '!suggest ' as the description.
    """
    if not description:
        await ctx.send("Please provide a description for your suggestion. Usage: `!suggest [description]`")
        return

    # Create a descriptive title and body for the GitHub issue
    title = f"Suggestion: {description[:50]}..." # Truncate title
    body = (
        f"**Suggestion from Discord**\n\n"
        f"**Submitted by:** {ctx.author.name} (ID: {ctx.author.id})\n\n"
        f"**Suggestion:**\n{description}"
    )
    
    await ctx.send(f"Submitting suggestion to GitHub...")
    
    # Use "enhancement" or "suggestion" as the label, depending on your repo's setup
    issue_url = create_github_issue(title, body, "suggestion") 
    
    if issue_url:
        embed = discord.Embed(
            title="Suggestion Submitted",
            description=f"✅ Thanks, {ctx.author.mention}! Your suggestion has been successfully submitted.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Issue URL", value=f"[View on GitHub]({issue_url})", inline=False)
        embed.add_field(name="Your Suggestion", value=f"```{description}```", inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ Sorry, {ctx.author.mention}. There was an error creating the GitHub issue. Please notify an admin.")

# --- Error Handling for Commands ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        if ctx.command.name == 'bug':
            await ctx.send("Please provide a description for the bug report. Usage: `!bug [description]`")
        elif ctx.command.name == 'suggest':
            await ctx.send("Please provide a description for your suggestion. Usage: `!suggest [description]`")
    elif isinstance(error, commands.CommandNotFound):
        # You can choose to ignore this or send a message
        pass
    else:
        # Log other errors to the console
        print(f"An error occurred with command {ctx.command}: {error}")
        await ctx.send("An unexpected error occurred. Please try again.")

# --- Run the Bot ---
if __name__ == "__main__":
    print("Starting bot...")
    bot.run(DISCORD_TOKEN)
