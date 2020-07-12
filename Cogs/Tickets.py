import asyncio, discord, datetime
from    datetime import timedelta
from    discord.ext import commands
from    Cogs import Settings, DisplayName

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
        self.all_tickets = {}
    
    class Ticket:
        """Constructor for a ticket. Ticket objets are made in the process_new_ticket() method"""
        def __init__(self, title, body, owner, date):
            expiry_days = timedelta(days=7)
            self.title = title
            self.body = body
            self.owner_id = owner.id
            self.owner_name = owner
            self.claimed_by = None
            self.date_made = date
            self.expires_on = date + expiry_days
            

    # Create a new ticket and add it to the queue
    @commands.command()
    async def newticket(self, ctx):
        def add_to_queue(ticket):
            """Make a list if one doesn't exist for a server
               Append the ticket to the list."""
            if self.all_tickets.get(ctx.guild.id) == None:
                self.all_tickets[ctx.guild.id] = [ticket]
            else:
                self.all_tickets[ctx.guild.id].append(ticket)
        
        def is_author(m):
            """Return true if the user entered the command"""
            return m.author == ctx.message.author
        
        async def check_response():
            return await self.bot.wait_for('message', check=is_author, timeout=30)
        
        async def get_ticket_item(intro, num):
            await ctx.channel.send(intro)
            item = await check_response()
            if len(item.content) <= num:
                msg = f'This is what I got: `{item.content}`\nIs this correct? (yes/no/stop)'
                await ctx.channel.send(msg)
                response = await check_response()
                
                if response.content.lower() == 'yes':
                    return item.content
                elif response.content.lower() == 'no':
                    await get_ticket_item(intro, num)
                elif response.content.lower() == 'stop':
                    await ctx.channel.send(f'No problem, {DisplayName.name(ctx.author)}! See you later!')
                    return None
                else:
                    await ctx.channel.send('I don\'t know what to say to that. Try making your ticket again.')
                    return None
            else:
                msg = f'Sorry, that message is too long. Try making it shorter than {num} characters.'
                await ctx.channel.send(msg)
                await get_ticket_item(intro, num)
        
        async def process_new_ticket():
            msg = f'Need some help, *{DisplayName.name(ctx.author)}*? Let\'s make a new ticket...\n'
            
            await ctx.channel.send(msg)
            
            msg = 'What do you need help with? This will be the title of your ticket, so please be concise (25 characters maximum).'
            
            title = await get_ticket_item(msg, 25)
            if title == None:
                return
                
            msg = 'OK! Tell me about your problem in 500 words or less.'
                
            body = await get_ticket_item(msg, 500)
            if body == None:
                return
                
            ticket = self.Ticket(title, body, ctx.message.author, datetime.date.today())
            msg = f'Your ticket was added to the queue. Someone will @ you if they claim your ticket.\nHere\'s what your ticket looks like:\n`Title:`\n{ticket.title}\n\n`Message:`\n{ticket.body}\n\n`Owner:`\n{ticket.owner_name}'
            msg += f'\n\n`Date created:`\n{ticket.date_made}\n\n`Expires on:`\n{ticket.expires_on}\n\n`Claimed by:`\n{ticket.claimed_by}'
            await ctx.channel.send(msg)
            if 
            add_to_queue(ticket)

        try:
            await process_new_ticket()
        except asyncio.TimeoutError:
            return await ctx.channel.send('I was waiting too long, sorry! Ask me again later if you still need help.')
    
    @commands.command()
    async def viewtickets(self, ctx):
        server = ctx.guild.id
        tickets = self.all_tickets[server]
        msg = f'Here are all the unclaimed tickets:\n\n'
        n = 0
        for ticket in tickets:
            n += 1
            msg += f'{n}. {ticket.title}\nCreated: {ticket.date_made}\nExpires: {ticket.expires_on}\n\n'
        await ctx.channel.send(msg)
    
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

    
