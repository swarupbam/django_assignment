from kudos.models import UserKudosCounter


def create_data():
    from kudos.models import Company
    from kudos.models import Employee

    c1 = Company.objects.create(name="Company 1")
    c2 = Company.objects.create(name="Company 2")

    for i in range(3):
        emp = Employee.objects.create(company=c1, username=f"user_{i}_company_{c1.id}")
        emp.set_password('123!')
        emp.save()
        UserKudosCounter.objects.create(user_id=emp)

    for i in range(3):
        emp = Employee.objects.create(company=c2, username=f"user_{i}_company_{c2.id}")
        emp.set_password('123!')
        emp.save()
        UserKudosCounter.objects.create(user_id=emp)
