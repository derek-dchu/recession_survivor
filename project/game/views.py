from django.views.generic import View
from django.shortcuts import render
from portfolio.models import Stock, Portfolio, Stock_owned


class Index( View ):
    def get( sefl, request ):
        return render( request, 'game/index.html')


class Round(View):
    #first time the round will be called by a GET, every time after will be a POST
    def get(self, request):
        #june 2009 and june 2008 exist in the db now, deleting june 2009 for easy querying
        extras = Stock.objects.filter(date__month=6, date__year=2009).delete()
        p = Portfolio.objects.create(user=request.user, balance=10000)        
        request.session['game_round'] = 0
        request.session['balance'] = 10000        
        return render(request, 'game/round.html', {'user':request.user, 'balance':'$10,000.00'})

    def post(self, request):
        if request.session['game_round'] == 12:
            return redirect('game/endgame.html')
        else:
            request.session['game_round'] += 1
            return render( request, 'game/round.html', {'user':request.user, 'balance':request.session['balance']})


class Endgame(View):
    def get(self, request):
        #sell all stocks, calculate new balance, show game transactions
        balance = request.session['balance']
        owned = Portfolio.objects.select_related('Stock_owned').filter(user=request.user)
        for stock in owned:
            current_priced_stock = Stock.objects.get(symbol=symbol, date__month=(request.session['game_round'] + 6) % 12)
            balance += (current_priced_stock.price * stock.amount)
            current_priced_stock.delete()
        portfolio = Portfolio.objects.filter(user=request.user).order_by('date')[0]
        trans = Transaction.objects.filter(portfolio=portfolio).order_by(date_created)
        return render( request, 'game/endgame.html', {"balance":balance, "history":trans})
