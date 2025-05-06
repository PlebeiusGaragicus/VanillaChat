import os
import json

import logging
logger = logging.getLogger(__name__)

from .VERSION import VERSION


class CommandHandler:
    @classmethod
    def _run(cls, command: str, arguments: str):
        """Handle a command and its arguments.
        
        Args:
            command: The command name without the leading slash
            arguments: String arguments for the command
        """
        # Try to get the method corresponding to the command
        method = getattr(cls, command, None)

        # If method exists and is callable, invoke it
        if callable(method) and not command.startswith('_'):
            return method(arguments)
        else:
            # return f"""# ⛓️‍💥\n`/{command}` command not found!\n## Commands available:\n{cls.help()}"""
            return f"""# ⛓️‍💥\n{cls.help()}"""

####################################################################################
    @classmethod
    def help(cls, args: str = None):
        """Get a list of commands."""
        # Generate usage text from available methods with a docstring
        command_list = [
            method for method in dir(cls)
            if callable(getattr(cls, method)) and not method.startswith("_")
        ]
        # Only show admin commands to admins
        command_list = [cmd for cmd in command_list if not cmd.endswith("_")]


        # Format as markdown with clear sections
        command_docs = []
        for cmd in sorted(command_list):
            # doc = getattr(cls, cmd).__doc__ or "No description available."
            doc = getattr(cls, cmd).__doc__ or None
            if doc:
                command_docs.append(f"- `/{cmd}` - {doc}")
            else:
                command_docs.append(f"- `/{cmd}`")


        return f"""### Commands Available

{chr(10).join(command_docs)}


Type any command to use it. For example: `/hi`
"""


####################################################################################
    @classmethod
    def cuss(cls, args: str = None):
        """Let off some steam... 😡"""
        return "fuck\n\nteehee"

####################################################################################
    @classmethod
    def version(cls, args: str = None):
        """Return the version of this graph."""
        return VERSION

####################################################################################
    @classmethod
    def hi(cls, args: str = None):
        """Tell the bot to say hello to you."""
        return f"""👋 Hi there!

You must be the `pleb` I've heard so much about...

I'm `Ollama`.  I'm just a simple chatbot agent.

Type `/about` to learn more.

Type `/help` to see a list of commands.

Or, just start asking questions!  I'm here to help.
"""

####################################################################################
    @classmethod
    def about(cls, args: str = None):
        """Get information about the agent."""
        return """
I am proof of concept LangGraph agent that accepts direct bitcoin payments from users.

I aim to be a useful assistant that anyone can use anonymously.

There's a lot I can do with more features being added all the time!

Try `/help` for a list of commands.

Here's my [source code on GitHub](https://github.com/PlebeiusGaragicus/PlebChatDocker)

Send me a message on nostr to chat about issues, features you'd like to see or anything AI-related.

```txt
npub1xegedgkkjf24pl4d76cdwhufacng5hapzjnrtgms3pyhlvmyqj9suym08k
```
"""


####################################################################################
# KEEP THIS
    # def usage(self, request, *args):
    #     """Track your **token usage** for this conversation."""

    #     is_admin = request.body['user']['role'] == 'admin'
    #     if is_admin:
    #         return "You're a system administrator - I don't track your usage!\nYou can use me for free!"

    #     lud16 = request.body['user']['email']
    #     if not lud16:
    #         return "⚠️ No user LUD16 provided."

    #     thread_id = request.body['chat_id']
    #     if not thread_id:
    #         return "⚠️ No thread ID provided."

    #     try:
    #         from .payment import get_usage
    #         usage = get_usage(lud16, thread_id)
    #         return f"User: `{lud16}`\nThread: `{thread_id}`\nYou have used: **`{0 if not usage else usage}`** generation tokens in this conversation."
    #     except Exception as e:
    #         return f"Error checking usage: {e}"

####################################################################################
    @classmethod
    def url(cls, args: str = None):
        # TODO: charge the user for this feature!!
        """Copy an article/website by providing the URL."""
        url = args if args else "No URL provided"
        return f"Scraping content from {url}"

# def url(request):
#     split = request.user_message.split(" ")
#     first_arg = split[1] if len(split) > 1 else None

#     if not first_arg:
#         return "⚠️ Please provide a URL.\n\n**Example:**\n```\n/url https://example.com\n```"

#     if first_arg.startswith("http://"):
#         return f"⚠️ The URL must start with `https://`\n\n**Example:**\n```\n/url https://example.com\n```"

#     if not first_arg.startswith("https://"):
#         first_arg = f"https://{first_arg}"

#     return f"""
# This command will scrape the provided url and reply with the "readability" text.

# This way, the contents of the url can be injected into the context of the conversation and can be discussed, summariezed, etc.

# This is a placeholder for the implementation of the url command.

# The URL you provided is: {first_arg}

# [Click here to view the content of the URL]({first_arg})

# The content of the URL will be displayed here.
# """
# #NOTE: providing just the url link like so:
# # [Click here to view the content of the URL]({first_arg})
# # will prepend the base url/c/ so that we can link TO CONVERSATIONS!!! WOW!



####################################################################################
    @classmethod
    def random(cls, args: str = None):
        """Generate a random number."""
        import random
        # If no argument provided, return random number between 1-100
        if args is None:
            random_number = random.randint(1, 100)
            return random_number
        else:
            try:
                digits = int(args)
                random_number = random.randint(1, 10**digits)
                return random_number
            except ValueError:
                return "Invalid number of digits. Please provide a single integer."

####################################################################################
    @classmethod
    def read(cls, args: str = None):
        return "Not yet implemented"
#     # TODO: I want to consider charging the user for intensive commands like this...
#     split = request.user_message.split(" ")
#     first_arg = split[1] if len(split) > 1 else None

#     #TODO: modularize this code.  Maybe have a _ensure_proper_url() function that can be reused in other commands.
#     if not first_arg:
#         return "⚠️ Please provide a URL.\n\n**Example:**\n```\n/article https://example.com\n```"

#     if first_arg.startswith("http://"):
#         return f"⚠️ The URL must start with `https://`\n\n**Example:**\n```\n/article https://example.com\n```"

#     if not first_arg.startswith("https://"):
#         first_arg = f"https://{first_arg}"

#     try:
#         from readability import Document
#         # url = "https://tftc.io/home-and-car-insurance-providers-retreating/"
#         # response = requests.get( url )
#         response = requests.get( first_arg )
#         doc = Document(response.content)

#         article_markdown_contents = f""

#         article_markdown_contents += doc.title()
#         article_markdown_contents += doc.summary()
#         article_markdown_contents += doc.content()



#         return f"""
# This command will scrape the provided url and reply with a summary of the content.

# The URL you provided is: {first_arg}

# Here's the article:

# ---

# {article_markdown_contents}
# """

#     except Exception as e:
#         return f"""error in scraping this URL: {e}"""