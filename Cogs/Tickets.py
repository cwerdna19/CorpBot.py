import asyncio, discord
from   discord.ext import commands
from   Cogs import Settings, DisplayName

def setup(bot):
    # Add the bot and deps
    settings = bot.get_cog("Settings")
    bot.add_cog(Tickets(bot, settings))

class Tickets(commands.Cog):

    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
        global DisplayName
        DisplayName = self.bot.get_cog("DisplayName")
        self.queues = {}

    # Create a new ticket and add it to the queue
    @commands.command()
    async def newticket(self, ctx):
        """
        TO DO:
        Add ctx.guild.id to self.queues if it does not exist.
        self.queues format:
        self.queues =
            { Servers:  {   1234: 
                                {   'Ticket1': { 'Title': 'My computer caught fire?', 'Body': 'I was cooking steak on my Intel CPU and the main board ignited. What should I do?', 'Owner': 'user.id', 'ClaimedBy': 'user.id' } },
                                {   'Ticket2': {} }
                        },
                        {   5678:
                                {{}}
                        }
            }
        """
        
        #ensure respondant is the author of the command
        def is_author(m):
            return m.author == ctx.message.author
        
        async def check_response():
            return await self.bot.wait_for('message', check=is_author, timeout=30)
        
        #felt cute might delete
        """
        async def yes_no_stop(m):
            if m.content.lower() == 'yes':
                return m.content
            elif m.content.lower() == 'no':
                # some func?
            elif m.content.lower() == 'stop':
                return await ctx.channel.send(f'No problem, {DisplayName.name(ctx.m.author)}! See you later!')
            else:
                return await ctx.channel.send('I don\'t know what to say to that. Try making your ticket again.')
        """
            
        async def get_ticket_body():
            msg = 'OK! Tell me about your problem in 500 words or less.'
            await ctx.channel.send(msg)
            body = await check_response()
            
            msg = 'Here\'s what I got:\n'
            msg += f'```\n{body.content}```'
            msg += 'Is this correct? (yes/no/stop)'
            await ctx.channel.send(msg)
            
            response = await check_response()
            
            #return await yes_no_stop(response)
            if len(body.content) <= 500:
                if response.content.lower() == 'yes':
                    return body.content
                elif response.content.lower() == 'no':
                    await get_ticket_body()
                elif response.content.lower() == 'stop':
                    await ctx.channel.send(f'No problem, {DisplayName.name(ctx.author)}! See you later!')
                    return None
                else:
                    await ctx.channel.send('I don\'t know what to say to that. Try making your ticket again.')
                    return None
            else:
                msg = 'Sorry, that message is too long.'
                await ctx.channel.send(msg)
                await get_body_title()
        
        async def get_ticket_title():
            msg = 'What do you need help with? This will be the title of your ticket, so please be concise (25 characters maximum).'
            await ctx.channel.send(msg)
            title = await check_response()
            if len(title.content) <= 25:
                msg = f'So you need help with `{title.content}`? (yes/no/stop)'
                await ctx.channel.send(msg)
                response = await check_response()
                
                if response.content.lower() == 'yes':
                    return title.content
                elif response.content.lower() == 'no':
                    await get_ticket_title()
                elif response.content.lower() == 'stop':
                    await ctx.channel.send(f'No problem, {DisplayName.name(ctx.author)}! See you later!')
                    return None
                else:
                    await ctx.channel.send('I don\'t know what to say to that. Try making your ticket again.')
                    return None
            else:
                msg = 'Sorry, that title is too long.'
                await ctx.channel.send(msg)
                await get_ticket_title()
        
        async def get_ticket_info():               
            msg = f'Need some help, *{DisplayName.name(ctx.author)}*? Let\'s make a new ticket...\n'
            
            await ctx.channel.send(msg)
            
            title = await get_ticket_title()
            if title == None:
                return
                
            body = await get_ticket_body()
            if body == None:
                return
                
            ticket = {'title': title, 'body': body}
            await ctx.channel.send(ticket)
        
        try:
            await get_ticket_info()
        except asyncio.TimeoutError:
            return await ctx.channel.send('I was waiting too long, sorry! Ask me again later if you still need help.')
    
    @commands.command()
    async def closeticket(self, ctx):
        #close a ticket and give credit to whoever helped you
        return
            
    @commands.command()
    async def delticket(self, ctx):
        #delete a ticket without giving credit (maybe implement as part of $closeticket)
        return
        
    @commands.command()
    async def editticket(self, ctx):
        #edit an existing ticket
        return
        
    @commands.command()
    async def claimticket(self, ctx):
        #claim a ticket from the queue that you want to work on
        return
        
    @commands.command()
    async def unclaimticket(self, ctx):
        #unclaim a ticket and add it back to the queue (maybe implement as part of $claimticket)
        return

    
