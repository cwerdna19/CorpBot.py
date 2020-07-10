""" Template copied from Examples cog. Heavily 'borrowed' from Hw cog."""
import asyncio, discord, random, time
from   discord.ext import commands
from   Cogs import Utils, Settings, DisplayName, UserTime, PickList, Nullify

def setup(bot):
    # Add the bot and deps
    settings = bot.get_cog("Settings")
    bot.add_cog(Tickets(bot, settings))

class Tickets(commands.Cog):

    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
        global Utils, DisplayName
        Utils = self.bot.get_cog("Utils")
        DisplayName = self.bot.get_cog("DisplayName")
        self.queues = {}
        
    #test
    @commands.command()
    async def guess(self, ctx):
        await ctx.channel.send('Guess a number between 1 and 10.')

        def is_correct(m):
            return m.author == ctx.message.author and m.content.isdigit()

        answer = random.randint(1, 10)

        try:
            guess = await self.bot.wait_for('message', check=is_correct)
        except asyncio.TimeoutError:
            return await ctx.channel.send('Sorry, you took too long it was {}.'.format(answer))

        if int(guess.content) == answer:
            await ctx.channel.send('You are right!')
        else:
            await ctx.channel.send('Oops. It is actually {}.'.format(answer))

    # Create a new ticket and add it to the queue
    @commands.command()
    async def newticket(self, ctx):
        
        #ensure respondant is the author of the command message
        def is_author(m):
            return m.author == ctx.message.author
    
        msg = 'Need some help, *{}*? Let\'s make a new ticket...\n\n'.format(DisplayName.name(ctx.author))
        msg += 'Firstly, what do you need help with? This will be the title of your ticket, so please be concise.\n\n'
        await ctx.channel.send(msg)
        
        async def check():
            try:
                c = await self.bot.wait_for('message', check=is_author, timeout=300)
                return c
            except asyncio.TimeoutError:
                return await ctx.channel.send('I waited too long, sorry! Ask me again later if you still need help.')
        chk = await check()
        while chk
        if len(chk.content) <= 25:
            msg = 'So you need help with {}? (yes/no/stop)'.format(title.content)
            await ctx.channel.send(msg)
            chk1 = await check()
            
            if chk1.content.lower() == 'yes':
                #continue making ticket
            elif chk1.content.lower() == 'no':
                #ask for the title again
            elif chk1.content.lower() == 'stop':
                #stop here
                break
        else:
            msg = 'Sorry, that title is too long.'
            await ctx.channel.send(msg)
            
    
    # def _stop_ticket()
    
    #def ticket_timeout()
    
    


"""        
    @commands.command()
    async def tickets():
        
        
    @commands.command()
    async def closeticket():
        return
"""