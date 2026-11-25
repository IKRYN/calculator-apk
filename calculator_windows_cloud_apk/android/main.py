import calendar
from datetime import date, timedelta
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout

def add_months(d, n):
    idx=d.month-1+n
    y=d.year+idx//12
    m=idx%12+1
    return date(y,m,min(d.day,calendar.monthrange(y,m)[1]))

def calculate(amount, rate, months, cap, monthly_add=0, start=None):
    start=start or date.today()
    end=add_months(start,months)
    daily=(rate/100)/365
    balance=amount; accrued=0.0; interest_total=0.0; adds_total=0.0; rows=[]
    month_interest=month_adds=month_cap=0.0; month_idx=1; current=start
    while current<end:
        if current.day==1 and current<end and (current.year,current.month)!=(end.year,end.month):
            balance+=monthly_add; adds_total+=monthly_add; month_adds+=monthly_add
        di=balance*daily; accrued+=di; month_interest+=di; interest_total+=di
        month_end=current.day==calendar.monthrange(current.year,current.month)[1]
        offset=(current.year-start.year)*12+current.month-start.month+1
        do_cap=(cap=="Ежедневно" or (cap=="Ежемесячно" and month_end)
                or (cap=="Раз в 3 месяца" and month_end and offset%3==0)
                or (cap=="Ежегодно" and month_end and offset%12==0))
        if current+timedelta(days=1)==end: do_cap=True
        if do_cap:
            balance+=accrued; month_cap+=accrued; accrued=0.0
        nxt=current+timedelta(days=1)
        if nxt.day==1 or nxt==end:
            rows.append((month_idx,nxt.strftime("%d.%m.%Y"),month_adds,month_interest,month_cap,balance,accrued))
            month_idx+=1; month_interest=month_adds=month_cap=0.0
        current=nxt
    yld=((balance-amount-adds_total)/(amount+adds_total)*100) if amount+adds_total else 0
    return balance,interest_total,adds_total,yld,(end-start).days,rows

KV = '''
<RootBox>:
    orientation: 'vertical'
    spacing: dp(8)
    padding: dp(12)
    ScrollView:
        size_hint: 1, 1
        do_scroll_x: False
        GridLayout:
            cols: 2
            spacing: dp(8)
            size_hint_y: None
            height: self.minimum_height
            Label:
                text: 'Сумма вклада, руб.'
                size_hint_y: None
                height: dp(42)
            TextInput:
                id: amount
                text: '100000'
                input_filter: 'float'
                multiline: False
                size_hint_y: None
                height: dp(42)
            Label:
                text: 'Ставка, %'
                size_hint_y: None
                height: dp(42)
            TextInput:
                id: rate
                text: '13'
                input_filter: 'float'
                multiline: False
                size_hint_y: None
                height: dp(42)
            Label:
                text: 'Срок (месяцы)'
                size_hint_y: None
                height: dp(42)
            TextInput:
                id: term
                text: '12'
                input_filter: 'int'
                multiline: False
                size_hint_y: None
                height: dp(42)
            Label:
                text: 'Капитализация'
                size_hint_y: None
                height: dp(42)
            Spinner:
                id: cap
                text: 'Ежемесячно'
                values: ['Ежедневно','Ежемесячно','Раз в 3 месяца','Ежегодно']
                size_hint_y: None
                height: dp(42)
            Label:
                text: 'Пополнение/мес., руб.'
                size_hint_y: None
                height: dp(42)
            TextInput:
                id: monthly
                text: '0'
                input_filter: 'float'
                multiline: False
                size_hint_y: None
                height: dp(42)
            Button:
                text: 'Рассчитать'
                size_hint_y: None
                height: dp(46)
                on_release: app.do_calculate()
            Button:
                text: 'Очистить'
                size_hint_y: None
                height: dp(46)
                on_release: app.clear_all()
    ScrollView:
        size_hint: 1, 1
        do_scroll_x: True
        Label:
            id: results
            text: 'Результаты появятся после расчёта.'
            size_hint: None, None
            width: max(dp(600), self.parent.width if self.parent else dp(600))
            height: max(self.texture_size[1], dp(220))
            text_size: self.width, None
            halign: 'left'
            valign: 'top'
'''
class RootBox(BoxLayout): pass

class DepositApp(App):
    def build(self):
        Builder.load_string(KV)
        return RootBox()
    def alert(self,msg):
        Popup(title="Ошибка",content=Label(text=msg),size_hint=(.85,.4)).open()
    def do_calculate(self):
        try:
            a=float(self.root.ids.amount.text.replace(',','.')); r=float(self.root.ids.rate.text.replace(',','.'))
            t=int(self.root.ids.term.text); m=float(self.root.ids.monthly.text.replace(',','.')) if self.root.ids.monthly.text.strip() else 0.0
            if a<=0: raise ValueError("Сумма должна быть положительной.")
            if r<0 or r>100: raise ValueError("Ставка должна быть от 0 до 100.")
            if t<1: raise ValueError("Срок должен быть не меньше 1 месяца.")
            if m<0: raise ValueError("Пополнение не может быть отрицательным.")
        except Exception as e:
            self.alert(str(e) or "Проверьте поля."); return
        bal,ints,adds,yld,days,rows=calculate(a,r,t,self.root.ids.cap.text,m)
        lines=["МЕСЯЦ | ДАТА | ПОПОЛНЕНИЕ | ПРОЦЕНТЫ | КАПИТАЛИЗАЦИЯ | БАЛАНС | НАКОПЛЕНО","-"*105]
        for row in rows:
            n,d,ad,ii,cc,bb,ac=row
            lines.append(f"{n} | {d} | {ad:,.2f} | {ii:,.2f} | {cc:,.2f} | {bb:,.2f} | {ac:,.2f}")
        lines += ["",f"Итоговый баланс: {bal:,.2f} руб.",f"Всего процентов: {ints:,.2f} руб.",
                  f"Сумма всех пополнений: {adds:,.2f} руб.",f"Итоговая сумма: {a+adds+ints:,.2f} руб.",
                  f"Эффективная доходность: {yld:.2f}%",f"Фактический срок: {days} дней"]
        self.root.ids.results.text="\n".join(lines)
    def clear_all(self):
        for key in ("amount","rate","term","monthly"): self.root.ids[key].text=""
        self.root.ids.cap.text="Ежемесячно"; self.root.ids.results.text="Результаты появятся после расчёта."

if __name__=="__main__": DepositApp().run()
