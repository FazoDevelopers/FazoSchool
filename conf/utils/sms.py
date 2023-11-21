from myconf.conf import get_model
from myconf import conf
def create_sms(parent,child,type_message):
    get_model(conf.MESSAGE).objects.create(parent=parent,child=child,type_message=type_message)

def create_debts_sms(parent,child,type_message,debts):
    debt=debts[0]
    get_model(conf.MESSAGE).objects.create(parent=parent,child=child,type_message=type_message,debt=debt)
    
def get_kirish_content(self):
    parent=self.parent
    child=self.child
    created_date=self.created_date
    message=f"""
    {child.first_name}.{child.last_name}
    Maktabga {created_date} kirdi!
    """

def get_chiqish_content(self):
    parent=self.parent
    child=self.child
    created_date=self.created_date
    message=f"""
    {child.first_name}.{child.last_name}
    Maktabdan {created_date} chiqdi!
    """

def get_debt_content(self):
    parent=self.parent
    child=self.child
    debt=self.debt
    created_date=self.created_date
    
    message=f"""
    {child.first_name}.{child.last_name}
    {debt.created_date} oy uchun {debt.balance} so'm qarzdor!
    """

#TODO sms